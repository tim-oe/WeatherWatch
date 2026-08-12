#!/usr/bin/env bash
# Pre-migration logical dump of the whole weather schema, stale tables included.
# Run on tec-weather after starting only mariadb (app units stay down).
#
# This is SQL, not a copy of /var/lib/mysql — 10.11 datadir files are not
# safe to drop onto 11.8 (mysql.user collation breakage).
#
# Usage:
#   sudo ./scripts/db-archive.sh
#   sudo MIG_ROOT=/mnt/clones/data/weather-migration ./scripts/db-archive.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

HOST="$(hostname -s)"
STAMP="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_NAME="weather_premigration_${HOST}_${STAMP}.sql.gz"
ARCHIVE_PATH="${DB_DIR}/${ARCHIVE_NAME}"
MANIFEST_PATH="${DB_DIR}/weather_premigration_${HOST}_${STAMP}.manifest"

write_manifest() {
  local version tz tables
  version="$(mysql_n -e 'SELECT VERSION()')"
  tz="$(mysql_n -e 'SELECT @@global.time_zone')"
  tables="$(list_weather_tables | tr '\n' ' ')"
  {
    echo "host=${HOST}"
    echo "created_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "archive=${ARCHIVE_NAME}"
    echo "database=${DATABASE}"
    echo "server_version=${version}"
    echo "global_time_zone=${tz}"
    echo "tables=${tables}"
  } >"${MANIFEST_PATH}"
}

main() {
  need_root
  resolve_clients
  ensure_staging
  require_server
  require_database
  write_manifest
  dump_weather "${ARCHIVE_PATH}"

  echo
  echo "Pre-migration archive complete (includes stale tables)."
  echo "  archive:  ${ARCHIVE_PATH}"
  echo "  checksum: ${ARCHIVE_PATH}.sha256"
  echo "  manifest: ${MANIFEST_PATH}"
  echo
  echo "Verify with:"
  echo "  (cd ${DB_DIR} && sha256sum -c ${ARCHIVE_NAME}.sha256)"
}

main "$@"
