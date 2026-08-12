#!/usr/bin/env bash
# Migration dump of the cleaned weather schema (after stale-table drops).
# Excludes apscheduler_jobs; the scheduler rebuilds jobs on startup.
#
# Usage:
#   sudo ./scripts/db-dump.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

HOST="$(hostname -s)"
STAMP="$(date +%Y%m%d_%H%M%S)"
DUMP_NAME="weather_${HOST}_${STAMP}.sql.gz"
DUMP_PATH="${DB_DIR}/${DUMP_NAME}"

main() {
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  local archive
  archive="$(latest_premigration_archive)"
  [[ -n "${archive}" ]] || die "no pre-migration archive in ${DB_DIR}; run db-archive.sh first"

  dump_weather "${DUMP_PATH}" --ignore-table="${DATABASE}.apscheduler_jobs"

  echo
  echo "Migration dump complete."
  echo "  dump:     ${DUMP_PATH}"
  echo "  checksum: ${DUMP_PATH}.sha256"
  echo "  archive:  ${archive}"
  echo
  echo "Verify with:"
  echo "  (cd ${DB_DIR} && sha256sum -c ${DUMP_NAME}.sha256)"
}

main "$@"
