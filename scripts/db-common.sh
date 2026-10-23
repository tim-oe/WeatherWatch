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

list_weather_tables() {
  mysql_n -e "SELECT TABLE_NAME FROM information_schema.TABLES
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_TYPE='BASE TABLE'
    ORDER BY TABLE_NAME"
}
