#!/usr/bin/env bash
# Diffable inventory of the weather schema on the source database.
# Run with sudo on the source host. Check the new database with db-verify.sh.
#
# Usage:
#   sudo ./scripts/db-inventory.sh
#   sudo ./scripts/db-inventory.sh /mnt/clones/data/weather-migration/inventory/weather_inventory_tec-desktop_rehearsal.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

usage() {
  cat <<EOF
Usage: sudo ./scripts/db-inventory.sh [outfile.txt]

Write a diffable inventory of the ${DATABASE} schema on the source database.

Arguments:
  outfile.txt   Optional. Default:
                ${INV_DIR}/weather_inventory_<host>_<stamp>.txt

Environment:
  MIG_ROOT   Staging root (default: /mnt/clones/data/weather-migration)

Compare that file to the new database with scripts/db-verify.sh.
EOF
}

if [[ $# -eq 1 && ( "${1}" == "-h" || "${1}" == "--help" ) ]]; then
  usage
  exit 0
fi
if [[ $# -gt 1 || ( $# -eq 1 && "${1}" == -* ) ]]; then
  usage >&2
  exit 1
fi

HOST="$(hostname -s)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_PATH="${1:-${INV_DIR}/weather_inventory_${HOST}_${STAMP}.txt}"

main() {
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  write_inventory "${OUT_PATH}" "${HOST}"
  echo "Inventory written to ${OUT_PATH}"
}

main "$@"
