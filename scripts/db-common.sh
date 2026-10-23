#!/usr/bin/env bash
# Shared helpers for scripts/db-*.sh. Sourced, not executed.
# Logical dump of the `weather` schema — do not copy /var/lib/mysql.
set -euo pipefail

MIG_ROOT="${MIG_ROOT:-/mnt/clones/data/weather-migration}"
DB_DIR="${MIG_ROOT}/db"
INV_DIR="${MIG_ROOT}/inventory"
DATABASE="${DATABASE:-weather}"
DUMP_NAME="${DUMP_NAME:-weather.sql}"

_DB_COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${_DB_COMMON_DIR}/.." && pwd)"
AQI_CLEAN_SQL="${REPO_ROOT}/sql/sp/aqi_clean.sql"

# Tables created by sql/schema/ plus the pyway history table.
# Anything else in `weather` is treated as stale by db-stale-tables.sh.
CANONICAL_TABLES=(
  outdoor_sensor
  indoor_sensor
  aqi_sensor
  light_sensor
  pi_metrics
  sdr_metrics
  sonic_reading
  solar_reading
  solar_temperature_sensor
  solar_temperature_reading
  apscheduler_jobs
  pyway
)

die() {
  echo "ERROR: $*" >&2
  exit 1
}

need_root() {
  [[ "${EUID}" -eq 0 ]] || die "run as root (unix_socket auth to MariaDB)"
}

ensure_staging() {
  mkdir -p "${DB_DIR}" "${INV_DIR}" "${MIG_ROOT}/files"
  [[ -w "${DB_DIR}" ]] || die "not writable: ${DB_DIR}"
  [[ -w "${INV_DIR}" ]] || die "not writable: ${INV_DIR}"
}

resolve_mysql_client() {
  if command -v mariadb >/dev/null 2>&1; then
    MYSQL_BIN=mariadb
  elif command -v mysql >/dev/null 2>&1; then
    MYSQL_BIN=mysql
  else
    die "neither mariadb nor mysql client is on PATH"
  fi
}

resolve_clients() {
  resolve_mysql_client

  if command -v mariadb-dump >/dev/null 2>&1; then
    DUMP_BIN=mariadb-dump
  elif command -v mysqldump >/dev/null 2>&1; then
    DUMP_BIN=mysqldump
  else
    die "neither mariadb-dump nor mysqldump is on PATH"
  fi
}

mysql_exec() {
  "${MYSQL_BIN}" --batch --raw "$@"
}

mysql_n() {
  "${MYSQL_BIN}" --batch --raw --skip-column-names "$@"
}

require_server() {
  mysql_n -e "SELECT 1" >/dev/null 2>&1 \
    || die "cannot connect to MariaDB (is the service started? sudo systemctl start mariadb)"
}

require_database() {
  local found
  found="$(mysql_n -e "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='${DATABASE}'")"
  [[ -n "${found}" ]] || die "database '${DATABASE}' does not exist"
}

# Remote connection for scripts that load the new database.
# Dump and inventory stay on the source and use the local root socket.
DB_HOST=""
DB_PORT=""
DB_USER=""
DB_PASSWORD=""
DB_NAME=""
REMOTE_POSITIONAL=()
CLIENT_DEFAULTS=""

cnf_quote() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '"%s"' "${s}"
}

sql_string() {
  local s="$1"
  s="${s//\'/\'\'}"
  printf "'%s'" "${s}"
}

cleanup_client_defaults() {
  if [[ -n "${CLIENT_DEFAULTS}" && -f "${CLIENT_DEFAULTS}" ]]; then
    rm -f "${CLIENT_DEFAULTS}"
  fi
}

parse_remote_args() {
  REMOTE_POSITIONAL=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --host|--port|--user|--password|--database)
        local flag="$1"
        [[ $# -ge 2 ]] || { echo "ERROR: ${flag} requires a value" >&2; usage >&2; exit 1; }
        local value="$2"
        if [[ -z "${value}" || "${value}" == --* ]]; then
          echo "ERROR: ${flag} requires a value" >&2
          usage >&2
          exit 1
        fi
        case "${flag}" in
          --host) DB_HOST="${value}" ;;
          --port) DB_PORT="${value}" ;;
          --user) DB_USER="${value}" ;;
          --password) DB_PASSWORD="${value}" ;;
          --database) DB_NAME="${value}" ;;
        esac
        shift 2
        ;;
      --host=*|--port=*|--user=*|--password=*|--database=*)
        local key="${1%%=*}"
        local value="${1#*=}"
        if [[ -z "${value}" ]]; then
          echo "ERROR: ${key} requires a value" >&2
          usage >&2
          exit 1
        fi
        case "${key}" in
          --host) DB_HOST="${value}" ;;
          --port) DB_PORT="${value}" ;;
          --user) DB_USER="${value}" ;;
          --password) DB_PASSWORD="${value}" ;;
          --database) DB_NAME="${value}" ;;
        esac
        shift
        ;;
      *)
        REMOTE_POSITIONAL+=("$1")
        shift
        ;;
    esac
  done
}

require_remote_config() {
  local -a missing=()
  [[ -n "${DB_HOST}" ]] || missing+=("--host")
  [[ -n "${DB_PORT}" ]] || missing+=("--port")
  [[ -n "${DB_USER}" ]] || missing+=("--user")
  [[ -n "${DB_PASSWORD}" ]] || missing+=("--password")
  [[ -n "${DB_NAME}" ]] || missing+=("--database")
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "ERROR: missing ${missing[*]}" >&2
    usage >&2
    exit 1
  fi
  [[ "${DB_PORT}" =~ ^[0-9]+$ ]] || { echo "ERROR: --port must be a number" >&2; usage >&2; exit 1; }
  [[ "${DB_PASSWORD}" != *$'\n'* ]] || die "--password cannot contain a newline"
  DATABASE="${DB_NAME}"
}

prepare_remote_client() {
  resolve_mysql_client
  CLIENT_DEFAULTS="$(mktemp)"
  chmod 600 "${CLIENT_DEFAULTS}"
  trap cleanup_client_defaults EXIT
  {
    echo "[client]"
    echo "protocol=tcp"
    printf 'host=%s\n' "$(cnf_quote "${DB_HOST}")"
    printf 'port=%s\n' "${DB_PORT}"
    printf 'user=%s\n' "$(cnf_quote "${DB_USER}")"
    printf 'password=%s\n' "$(cnf_quote "${DB_PASSWORD}")"
  } >"${CLIENT_DEFAULTS}"
}

remote_mysql() {
  "${MYSQL_BIN}" --defaults-extra-file="${CLIENT_DEFAULTS}" --batch --raw "$@"
}

remote_mysql_n() {
  remote_mysql --skip-column-names "$@"
}

require_remote_server() {
  remote_mysql_n -e "SELECT 1" >/dev/null 2>&1 \
    || die "cannot connect to ${DB_USER}@${DB_HOST}:${DB_PORT}"
}

write_checksum() {
  local path="$1"
  local dir base
  dir="$(dirname "${path}")"
  base="$(basename "${path}")"
  (
    cd "${dir}"
    sha256sum "${base}" >"${base}.sha256"
  )
}

verify_checksum() {
  local path="$1"
  local dir base sha
  dir="$(dirname "${path}")"
  base="$(basename "${path}")"
  sha="${dir}/${base}.sha256"
  [[ -f "${sha}" ]] || die "checksum missing: ${sha}"
  echo "Verifying ${sha}"
  (cd "${dir}" && sha256sum -c "${base}.sha256")
}

default_dump_path() {
  printf '%s\n' "${DB_DIR}/${DUMP_NAME}"
}

latest_premigration_archive() {
  ls -1t "${DB_DIR}"/weather_premigration_*.sql 2>/dev/null | head -n1 || true
}

# No positional parameters. Zero arguments continues.
# -h/--help prints usage and exits 0. Anything else prints usage and exits 1.
check_no_args() {
  if [[ $# -eq 0 ]]; then
    return 0
  fi
  if [[ $# -eq 1 && ( "${1}" == "-h" || "${1}" == "--help" ) ]]; then
    usage
    exit 0
  fi
  usage >&2
  exit 1
}

dump_weather() {
  # First arg is the output .sql path on the share. Remaining args are extra
  # mariadb-dump flags. The file is plain SQL; the share has the space and
  # restore reads it directly.
  local out="$1"
  shift
  local -a extra=("$@")

  echo "Dumping ${DATABASE} -> ${out}"
  echo "  client: ${DUMP_BIN}"
  "${DUMP_BIN}" \
    --single-transaction \
    --quick \
    --hex-blob \
    --routines \
    --events \
    --triggers \
    --default-character-set=utf8mb4 \
    "${extra[@]}" \
    --databases "${DATABASE}" \
    >"${out}"
  write_checksum "${out}"
  echo "  size: $(du -h "${out}" | awk '{print $1}')"
}

query_exec() {
  "${Q_EXEC:-mysql_exec}" "$@"
}

query_n() {
  "${Q_N:-mysql_n}" "$@"
}

sql_ident() {
  local s="$1"
  s="${s//\`/\`\`}"
  printf '`%s`' "${s}"
}

list_weather_tables() {
  query_n -e "SELECT TABLE_NAME FROM information_schema.TABLES
    WHERE TABLE_SCHEMA=$(sql_string "${DATABASE}") AND TABLE_TYPE='BASE TABLE'
    ORDER BY TABLE_NAME"
}

inventory_has_column() {
  local table="$1" col="$2"
  local n
  n="$(query_n -e "SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA=$(sql_string "${DATABASE}")
      AND TABLE_NAME=$(sql_string "${table}")
      AND COLUMN_NAME=$(sql_string "${col}")")"
  [[ "${n}" == "1" ]]
}

inventory_emit_table() {
  local table="$1"
  local ident
  ident="$(sql_ident "${table}")"
  echo "===== TABLE ${table} ====="

  query_exec -e "SELECT
      TABLE_ROWS AS approx_rows,
      DATA_LENGTH AS data_bytes,
      INDEX_LENGTH AS index_bytes,
      CREATE_TIME,
      TABLE_COLLATION
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA=$(sql_string "${DATABASE}") AND TABLE_NAME=$(sql_string "${table}")\G"

  echo "-- COUNT(*)"
  query_exec "${DATABASE}" -e "SELECT COUNT(*) AS row_count FROM ${ident}"

  if inventory_has_column "${table}" id; then
    echo "-- MAX(id)"
    query_exec "${DATABASE}" -e "SELECT MAX(id) AS max_id FROM ${ident}"
  fi

  if inventory_has_column "${table}" read_time; then
    echo "-- MIN/MAX(read_time)"
    query_exec "${DATABASE}" -e "SELECT MIN(read_time) AS min_read_time, MAX(read_time) AS max_read_time FROM ${ident}"
  fi

  echo "-- SHOW CREATE TABLE"
  query_exec "${DATABASE}" -e "SHOW CREATE TABLE ${ident}\G"

  echo "-- PARTITIONS"
  query_exec -e "SELECT PARTITION_NAME, TABLE_ROWS, PARTITION_DESCRIPTION
    FROM information_schema.PARTITIONS
    WHERE TABLE_SCHEMA=$(sql_string "${DATABASE}") AND TABLE_NAME=$(sql_string "${table}")
      AND PARTITION_NAME IS NOT NULL
    ORDER BY PARTITION_ORDINAL_POSITION"
  echo
}

write_inventory() {
  local out="$1"
  local label="$2"
  mkdir -p "$(dirname "${out}")"
  {
    echo "host=${label}"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "database=${DATABASE}"
    query_exec -e "SELECT VERSION() AS server_version,
      @@global.time_zone AS global_time_zone,
      @@session.time_zone AS session_time_zone,
      NOW() AS now_local,
      UTC_TIMESTAMP() AS now_utc\G"
    echo

    local table
    while IFS= read -r table; do
      [[ -n "${table}" ]] || continue
      inventory_emit_table "${table}"
    done < <(list_weather_tables)

    echo "===== ROUTINES ====="
    query_exec -e "SELECT ROUTINE_NAME, ROUTINE_TYPE
      FROM information_schema.ROUTINES
      WHERE ROUTINE_SCHEMA=$(sql_string "${DATABASE}")
      ORDER BY ROUTINE_NAME"
  } >"${out}"
}

# Lines that should match across a source dump and the new database.
# Drops host, clock, server version, storage sizes, and SHOW CREATE TABLE.
inventory_facts() {
  local file="$1"
  awk -F '\t' -v OFS='\t' '
    /^database=/ { print; next }
    /^[[:space:]]*global_time_zone:/ {
      sub(/^[[:space:]]*global_time_zone:[[:space:]]*/, "")
      printf "global_time_zone=%s\n", $0
      next
    }
    /^[[:space:]]*session_time_zone:/ {
      sub(/^[[:space:]]*session_time_zone:[[:space:]]*/, "")
      printf "session_time_zone=%s\n", $0
      next
    }
    /^===== ROUTINES =====/ { print; capture=1; in_part=0; next }
    /^===== TABLE / { print; capture=0; in_part=0; next }
    /^-- PARTITIONS$/ { print; in_part=1; capture=0; next }
    /^-- COUNT\(\*\)/ || /^-- MAX\(id\)/ || /^-- MIN\/MAX\(read_time\)/ {
      print; capture=1; in_part=0; next
    }
    /^-- / { capture=0; in_part=0; next }
    in_part && $0 != "" {
      if ($1 == "PARTITION_NAME") {
        print "PARTITION_NAME", "PARTITION_DESCRIPTION"
        next
      }
      if (NF >= 3) print $1, $3
      else print
      next
    }
    capture && $0 != "" { print }
  ' "${file}"
}
