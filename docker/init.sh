#!bin/bash

if [ -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "Bench already exists, skipping init"
    cd frappe-bench
    bench start
    exit 0
fi

echo "Creating new bench..."

bench init --skip-redis-config-generation frappe-bench --frappe-branch version-15

cd frappe-bench

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Remove redis, watch from Procfile
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

# Get all apps
bench get-app erpnext --branch version-15
bench get-app lending --branch version-15
bench get-app https://github.com/frappe/drive.git --branch main
bench get-app https://github.com/frappe/telephony.git --branch develop
bench get-app helpdesk --branch main
bench get-app insights --branch version-3
bench get-app https://github.com/clefincode/clefincode_chat.git --branch develop
bench get-app /home/frappe/frappe-crm

# Create site
bench new-site crm.localhost \
    --force \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket

# Install all apps
bench --site crm.localhost install-app erpnext
bench --site crm.localhost install-app lending
bench --site crm.localhost install-app drive
bench --site crm.localhost install-app telephony
bench --site crm.localhost install-app helpdesk
bench --site crm.localhost install-app insights
bench --site crm.localhost install-app clefincode_chat
bench --site crm.localhost install-app crm

# Site config
bench --site crm.localhost set-config developer_mode 1
bench --site crm.localhost set-config mute_emails 1
bench --site crm.localhost set-config server_script_enabled 1
bench --site crm.localhost clear-cache
bench use crm.localhost

bench start
