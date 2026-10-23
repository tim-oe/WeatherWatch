#!/usr/bin/env bash
# Create the target database on the new server.
# Run from a host that can reach that server. Connection settings are the
# new database's own host, port, user, password, and database name.
# Does not create application accounts and does not run pyway migrate.
#
# Usage:
#   ./scripts/db-init.sh --host HOST --port PORT --user USER --password PASS --database NAME
# Running without those settings prints this syntax.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

usage() {
  cat <<EOF
Usage: ./scripts/db-init.sh --host HOST --port PORT --user USER --password PASS --database NAME

Create the target database on the new server over TCP.

Connection:
  --host       Server address
  --port       Server port
  --user       Account that can create the database
  --password   Password for that account
  --database   Database name to create

The account is the new database login, not the application login.
EOF
}

sql_ident() {
  local s="$1"
  s="${s//\`/\`\`}"
  printf '`%s`' "${s}"
}

main() {
  parse_remote_args "$@"
  if [[ ${#REMOTE_POSITIONAL[@]} -gt 0 ]]; then
    echo "ERROR: unexpected argument: ${REMOTE_POSITIONAL[0]}" >&2
    usage >&2
    exit 1
  fi
  require_remote_config
  prepare_remote_client
  require_remote_server

  local q_db
  q_db="$(sql_ident "${DATABASE}")"
  echo "Creating database ${DATABASE} on ${DB_USER}@${DB_HOST}:${DB_PORT}"
  remote_mysql -e "CREATE DATABASE IF NOT EXISTS ${q_db}"

  echo
  remote_mysql -e "SELECT SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
    FROM information_schema.SCHEMATA
    WHERE SCHEMA_NAME=$(sql_string "${DATABASE}")"
  echo
  echo "Init complete. Load the dump next:"
  echo "  ${SCRIPT_DIR}/db-restore.sh --host ${DB_HOST} --port ${DB_PORT} --user ${DB_USER} --password PASS --database ${DATABASE} $(default_dump_path)"
}

main "$@"
