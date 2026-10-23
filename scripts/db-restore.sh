#!/usr/bin/env bash
# Load a weather schema dump into the new database.
# Run from a host that can reach that server. The dump is read from the
# path given here (the clones share). Connection settings are the new
# database's own host, port, user, password, and database name.
#
# Usage:
#   ./scripts/db-restore.sh --host HOST --port PORT --user USER --password PASS --database NAME /mnt/clones/data/weather-migration/db/weather.sql
#   ./scripts/db-restore.sh --host HOST --port PORT --user USER --password PASS --database NAME /mnt/clones/data/weather-migration/db/weather.sql --force
# Running without the connection settings or the dump path prints this syntax.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

FORCE=0
DUMP_PATH=""

usage() {
  cat <<EOF
Usage: ./scripts/db-restore.sh --host HOST --port PORT --user USER --password PASS --database NAME <dump.sql> [--force]

Load a plain SQL dump into the new database over TCP.

Connection:
  --host       Server address
  --port       Server port
  --user       Account that can create and load the schema
  --password   Password for that account
  --database   Database name to load

Arguments:
  dump.sql     SQL file to read. Typical path:
               ${DB_DIR}/${DUMP_NAME}
  --force      Replace tables when the database is not empty

The account is the new database login, not the application login.
EOF
}

parse_args() {
  local arg
  parse_remote_args "$@"
  if [[ ${#REMOTE_POSITIONAL[@]} -eq 0 ]]; then
    return
  fi
  for arg in "${REMOTE_POSITIONAL[@]}"; do
    case "${arg}" in
      --force)
        FORCE=1
        ;;
      -*)
        echo "ERROR: unknown option: ${arg}" >&2
        usage >&2
        exit 1
        ;;
      *)
        if [[ -n "${DUMP_PATH}" ]]; then
          echo "ERROR: unexpected argument: ${arg}" >&2
          usage >&2
          exit 1
        fi
        DUMP_PATH="${arg}"
        ;;
    esac
  done
}

table_count() {
  local q
  q="$(sql_string "${DATABASE}")"
  remote_mysql_n -e "SELECT COUNT(*) FROM information_schema.TABLES
    WHERE TABLE_SCHEMA=${q} AND TABLE_TYPE='BASE TABLE'"
}

main() {
  parse_args "$@"
  require_remote_config
  if [[ -z "${DUMP_PATH}" ]]; then
    echo "ERROR: missing dump.sql" >&2
    usage >&2
    exit 1
  fi
  [[ -f "${DUMP_PATH}" ]] || die "dump not found: ${DUMP_PATH}"
  verify_checksum "${DUMP_PATH}"

  prepare_remote_client
  require_remote_server

  local existing
  existing="$(table_count)"
  if [[ "${existing}" != "0" && "${FORCE}" -ne 1 ]]; then
    die "${DATABASE} already has ${existing} table(s). Pass --force to replace them from the dump."
  fi

  echo "Restoring ${DUMP_PATH} into ${DB_USER}@${DB_HOST}:${DB_PORT}/${DATABASE}"
  remote_mysql <"${DUMP_PATH}"
  echo "Dump loaded."

  if [[ -f "${AQI_CLEAN_SQL}" ]]; then
    echo "Re-applying ${AQI_CLEAN_SQL}"
    remote_mysql "${DATABASE}" <"${AQI_CLEAN_SQL}"
  else
    echo "WARN: ${AQI_CLEAN_SQL} not found; skipped aqi_clean re-apply" >&2
  fi

  echo
  echo "Tables now in ${DATABASE}:"
  remote_mysql "${DATABASE}" -e "SHOW TABLES"
  echo
  echo "Routines:"
  remote_mysql -e "SELECT ROUTINE_NAME, ROUTINE_TYPE
    FROM information_schema.ROUTINES
    WHERE ROUTINE_SCHEMA=$(sql_string "${DATABASE}")"
  echo
  echo "Restore complete on ${DB_HOST}:${DB_PORT}/${DATABASE}."
}

main "$@"
