#!/usr/bin/env bash
# Logical dump of the entire weather schema as it stands: every table
# (including apscheduler_jobs and any stale *_old / *_tmp leftovers),
# plus routines, events, and triggers.
# Writes a fixed path so each run overwrites the file restore reads.
#
# Usage:
#   sudo ./scripts/db-dump.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

usage() {
  cat <<EOF
Usage: sudo ./scripts/db-dump.sh

Write a plain SQL dump of the ${DATABASE} schema to:
  ${DB_DIR}/${DUMP_NAME}

Environment:
  MIG_ROOT   Staging root (default: /mnt/clones/data/weather-migration)
EOF
}

main() {
  check_no_args "$@"
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database

  dump_weather "$(default_dump_path)"

  echo
  echo "Dump complete (full ${DATABASE} schema)."
  echo "  dump:     $(default_dump_path)"
  echo "  checksum: $(default_dump_path).sha256"
  echo
  echo "Verify with:"
  echo "  (cd ${DB_DIR} && sha256sum -c ${DUMP_NAME}.sha256)"
  echo "Load it into the new database from a host that can reach it:"
  echo "  ${SCRIPT_DIR}/db-restore.sh --host HOST --port PORT --user USER --password PASS --database NAME $(default_dump_path)"
}

main "$@"
