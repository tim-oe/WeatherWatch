#!/usr/bin/env bash
# Create the weather database and app/pyway users from /etc/environment.
# Run on tec-weather2 as root after files-restore.sh and with mariadb started.
# Does not run pyway migrate — the dump carries schema and pyway history.
#
# Usage:
#   sudo ./scripts/db-init.sh
#   sudo ENV_FILE=/etc/environment ./scripts/db-init.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=db-common.sh
source "${SCRIPT_DIR}/db-common.sh"

ENV_FILE="${ENV_FILE:-/etc/environment}"
DB_USER_HOST="${DB_USER_HOST:-%}"

read_env() {
  local key="$1"
  local line val
  [[ -f "${ENV_FILE}" ]] || die "missing ${ENV_FILE} (run files-restore.sh first)"
  line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n1 || true)"
  [[ -n "${line}" ]] || die "${key} not set in ${ENV_FILE}"
  val="${line#*=}"
  val="${val%\"}"
  val="${val#\"}"
  val="${val%\'}"
  val="${val#\'}"
  [[ -n "${val}" ]] || die "${key} is empty in ${ENV_FILE}"
  printf '%s' "${val}"
}

sql_quote() {
  local s="$1"
  s="${s//\'/\'\'}"
  printf "'%s'" "${s}"
}

main() {
  need_root
  resolve_clients
  require_server

  [[ -f "${ENV_FILE}" ]] || die "missing ${ENV_FILE} (run files-restore.sh first)"

  local db_name app_user app_pass pyway_user pyway_pass
  db_name="$(grep -E '^WW_DB_NAME=' "${ENV_FILE}" | tail -n1 | cut -d= -f2- || true)"
  db_name="${db_name:-${DATABASE}}"
  app_user="$(read_env WW_DB_USERNAME)"
  app_pass="$(read_env WW_DB_PASSWORD)"
  pyway_user="$(read_env PYWAY_DATABASE_USERNAME)"
  pyway_pass="$(read_env PYWAY_DATABASE_PASSWORD)"

  local q_db q_host q_app_user q_app_pass q_pyway_user q_pyway_pass
  q_db="\`${db_name//\`/\`\`}\`"
  q_host="$(sql_quote "${DB_USER_HOST}")"
  q_app_user="$(sql_quote "${app_user}")"
  q_app_pass="$(sql_quote "${app_pass}")"
  q_pyway_user="$(sql_quote "${pyway_user}")"
  q_pyway_pass="$(sql_quote "${pyway_pass}")"

  echo "Creating database ${db_name} and users from ${ENV_FILE}"
  echo "  app user:    ${app_user}@${DB_USER_HOST}"
  echo "  pyway user:  ${pyway_user}@${DB_USER_HOST}"

  "${MYSQL_BIN}" --batch <<SQL
CREATE DATABASE IF NOT EXISTS ${q_db};

CREATE USER IF NOT EXISTS ${q_app_user}@${q_host} IDENTIFIED BY ${q_app_pass};
ALTER USER ${q_app_user}@${q_host} IDENTIFIED BY ${q_app_pass};
GRANT LOCK TABLES, DROP, SELECT, INSERT, DELETE, UPDATE, EXECUTE, CREATE TEMPORARY TABLES
  ON ${q_db}.* TO ${q_app_user}@${q_host};

CREATE USER IF NOT EXISTS ${q_pyway_user}@${q_host} IDENTIFIED BY ${q_pyway_pass};
ALTER USER ${q_pyway_user}@${q_host} IDENTIFIED BY ${q_pyway_pass};
GRANT ALL PRIVILEGES ON ${q_db}.* TO ${q_pyway_user}@${q_host};

FLUSH PRIVILEGES;
SQL

  echo
  echo "Users:"
  mysql_exec -e "SELECT User, Host FROM mysql.user
    WHERE User IN ($(sql_quote "${app_user}"), $(sql_quote "${pyway_user}"))
    ORDER BY User, Host"
  echo
  echo "Grants:"
  mysql_exec -e "SHOW GRANTS FOR ${q_app_user}@${q_host}"
  mysql_exec -e "SHOW GRANTS FOR ${q_pyway_user}@${q_host}"
  echo
  echo "Init complete. Do not run pyway migrate; restore the dump next:"
  echo "  sudo ${SCRIPT_DIR}/db-restore.sh"
}

main "$@"
