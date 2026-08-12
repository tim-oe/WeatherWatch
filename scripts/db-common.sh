#!/usr/bin/env bash
# Shared helpers for scripts/db-*.sh. Sourced, not executed.
# Logical dump of the `weather` schema — do not copy /var/lib/mysql.
set -euo pipefail

MIG_ROOT="${MIG_ROOT:-/mnt/clones/data/weather-migration}"
DB_DIR="${MIG_ROOT}/db"
INV_DIR="${MIG_ROOT}/inventory"
DATABASE="${DATABASE:-weather}"
GZIP_LEVEL="${GZIP_LEVEL:-6}"

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

resolve_clients() {
  if command -v mariadb >/dev/null 2>&1; then
    MYSQL_BIN=mariadb
  elif command -v mysql >/dev/null 2>&1; then
    MYSQL_BIN=mysql
  else
    die "neither mariadb nor mysql client is on PATH"
  fi

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

latest_premigration_archive() {
  ls -1t "${DB_DIR}"/weather_premigration_*.sql.gz 2>/dev/null | head -n1 || true
}

latest_migration_dump() {
  # Migration dumps are weather_<host>_<stamp>.sql.gz, not premigration keepsakes.
  ls -1t "${DB_DIR}"/weather_*.sql.gz 2>/dev/null \
    | grep -v '/weather_premigration_' \
    | head -n1 || true
}

dump_weather() {
  # Args: extra mariadb-dump flags, then the output .sql.gz path as last arg.
  local out="$1"
  shift
  local -a extra=("$@")

  echo "Dumping ${DATABASE} -> ${out}"
  echo "  client: ${DUMP_BIN}  gzip -${GZIP_LEVEL}"
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
    | gzip "-${GZIP_LEVEL}" >"${out}"
  write_checksum "${out}"
  echo "  size: $(du -h "${out}" | awk '{print $1}')"
}

list_weather_tables() {
  mysql_n -e "SELECT TABLE_NAME FROM information_schema.TABLES
    WHERE TABLE_SCHEMA='${DATABASE}' AND TABLE_TYPE='BASE TABLE'
    ORDER BY TABLE_NAME"
}
