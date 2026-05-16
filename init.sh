#!/bin/bash
set -e

cd /workspace

if [ -d "/workspace/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists, skipping init"
    cd /workspace/frappe-bench
    bench start
    exit 0
fi

echo "Creating new bench..."
bench init --skip-redis-config-generation frappe-bench --version version-15
cd /workspace/frappe-bench

# Use containers instead of localhost or external services
MYSQL_HOST=${MYSQL_HOST:-mariadb}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-admin}
MYSQL_DB_NAME=${MYSQL_DB_NAME:-}

REDIS_CACHE=${REDIS_CACHE:-${REDIS_URI:-redis://redis:6379}}
REDIS_QUEUE=${REDIS_QUEUE:-${REDIS_URI:-redis://redis:6379}}
REDIS_SOCKETIO=${REDIS_SOCKETIO:-${REDIS_URI:-redis://redis:6379}}

bench set-mariadb-host ${MYSQL_HOST}
bench set-redis-cache-host ${REDIS_CACHE}
bench set-redis-queue-host ${REDIS_QUEUE}
bench set-redis-socketio-host ${REDIS_SOCKETIO}

# Remove redis and watch from Procfile if present
if [ -f ./Procfile ]; then
  sed -i '/redis/d' ./Procfile || true
  sed -i '/watch/d' ./Procfile || true
fi

# Install local CRM app if available, otherwise fetch remote app
if [ -d "/workspace/crm" ]; then
  rm -rf ./apps/crm
  mkdir -p ./apps
  cp -R /workspace/crm ./apps/crm
else
  bench get-app crm https://github.com/frappe/crm.git --branch main
fi

bench new-site crm.localhost \
    --force \
    --mariadb-host ${MYSQL_HOST} \
    --mariadb-root-password ${MYSQL_ROOT_PASSWORD} \
    --admin-password ${ADMIN_PASSWORD:-admin} \
    --no-mariadb-socket \
    ${MYSQL_DB_NAME:+--db-name ${MYSQL_DB_NAME}}

bench --site crm.localhost install-app crm
bench --site crm.localhost set-config developer_mode 1
bench --site crm.localhost set-config mute_emails 1
bench --site crm.localhost set-config server_script_enabled 1
bench --site crm.localhost clear-cache
bench use crm.localhost

bench start