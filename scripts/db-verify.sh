#!/usr/bin/env bash
# Inventory the new database and compare it to a source inventory.
# Run from a host that can reach the new server. Connection settings are
# that database's own host, port, user, password, and database name.
#
# Usage:
#   ./scripts/db-verify.sh --host HOST --port PORT --user USER --password PASS --database NAME \
#     /mnt/clones/data/weather-migration/inventory/weather_inventory_tec-desktop_rehearsal.txt
# Running without the connection settings or the source inventory prints this syntax.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

SOURCE_INVENTORY=""
REMOTE_OUT=""

usage() {
  cat <<EOF
Usage: ./scripts/db-verify.sh --host HOST --port PORT --user USER --password PASS --database NAME <source-inventory.txt> [--output outfile.txt]

Inventory the new database and compare it to a source inventory from db-inventory.sh.

Connection:
  --host       Server address
  --port       Server port
  --user       Account that can read the schema
  --password   Password for that account
  --database   Database name to inventory

Arguments:
  source-inventory.txt   Inventory written on the source host
  --output outfile.txt   Optional remote inventory path. Default:
                         ${INV_DIR}/weather_inventory_<host>_<stamp>.txt

Compared: database name, time zones, row counts, max id, read_time range,
partition bounds, and routines. Server version, clock, storage size, and
SHOW CREATE TABLE are written to the remote inventory and are not compared.
EOF
}

parse_args() {
  local -a rest=()
  local i=0 arg
  parse_remote_args "$@"
  if [[ ${#REMOTE_POSITIONAL[@]} -eq 0 ]]; then
    return
  fi
  rest=("${REMOTE_POSITIONAL[@]}")
  while [[ ${i} -lt ${#rest[@]} ]]; do
    arg="${rest[${i}]}"
    case "${arg}" in
      --output)
        if [[ $((i + 1)) -ge ${#rest[@]} || -z "${rest[$((i + 1))]}" || "${rest[$((i + 1))]}" == --* ]]; then
          echo "ERROR: --output requires a value" >&2
          usage >&2
          exit 1
        fi
        REMOTE_OUT="${rest[$((i + 1))]}"
        i=$((i + 2))
        ;;
      -*)
        echo "ERROR: unknown option: ${arg}" >&2
        usage >&2
        exit 1
        ;;
      *)
        if [[ -n "${SOURCE_INVENTORY}" ]]; then
          echo "ERROR: unexpected argument: ${arg}" >&2
          usage >&2
          exit 1
        fi
        SOURCE_INVENTORY="${arg}"
        i=$((i + 1))
        ;;
    esac
  done
}

require_remote_database() {
  local found
  found="$(remote_mysql_n -e "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=$(sql_string "${DATABASE}")")"
  [[ -n "${found}" ]] || die "database '${DATABASE}' does not exist on ${DB_HOST}:${DB_PORT}"
}

main() {
  local stamp host_label src_facts dst_facts
  parse_args "$@"
  require_remote_config
  if [[ -z "${SOURCE_INVENTORY}" ]]; then
    echo "ERROR: missing source-inventory.txt" >&2
    usage >&2
    exit 1
  fi
  [[ -f "${SOURCE_INVENTORY}" ]] || die "source inventory not found: ${SOURCE_INVENTORY}"

  stamp="$(date +%Y%m%d_%H%M%S)"
  host_label="${DB_HOST//\//_}"
  if [[ -z "${REMOTE_OUT}" ]]; then
    ensure_staging
    REMOTE_OUT="${INV_DIR}/weather_inventory_${host_label}_${stamp}.txt"
  fi

  prepare_remote_client
  require_remote_server
  require_remote_database

  Q_EXEC=remote_mysql
  Q_N=remote_mysql_n
  write_inventory "${REMOTE_OUT}" "${host_label}"
  echo "Remote inventory written to ${REMOTE_OUT}"

  src_facts="$(mktemp)"
  dst_facts="$(mktemp)"
  trap "cleanup_client_defaults; rm -f $(printf '%q' "${src_facts}") $(printf '%q' "${dst_facts}")" EXIT
  inventory_facts "${SOURCE_INVENTORY}" >"${src_facts}"
  inventory_facts "${REMOTE_OUT}" >"${dst_facts}"

  echo "Comparing ${SOURCE_INVENTORY} to ${REMOTE_OUT}"
  if ! diff -u "${src_facts}" "${dst_facts}"; then
    echo "Verification failed. Counts, time zones, partition bounds, or routines differ." >&2
    exit 1
  fi
  echo "Verification passed."
}

main "$@"
