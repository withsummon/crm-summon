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

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

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
    --mariadb-root-password ${MYSQL_ROOT_PASSWORD:-admin} \
    --admin-password ${ADMIN_PASSWORD:-admin} \
    --no-mariadb-socket

bench --site crm.localhost install-app crm
bench --site crm.localhost set-config developer_mode 1
bench --site crm.localhost set-config mute_emails 1
bench --site crm.localhost set-config server_script_enabled 1
bench --site crm.localhost clear-cache
bench use crm.localhost

bench start