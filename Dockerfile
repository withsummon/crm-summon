FROM frappe/bench:latest AS frontend-builder

USER root

WORKDIR /build/crm

COPY . .

RUN chown -R frappe:frappe /build/crm

USER frappe

WORKDIR /build/crm/frontend

RUN yarn install --frozen-lockfile
RUN yarn build


FROM frappe/erpnext-worker:latest

USER root

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

RUN cat > /home/frappe/frappe-bench/configurator.py <<'EOF'
#!/usr/bin/env python3
import json
from pathlib import Path

sites_dir = Path("/home/frappe/frappe-bench/sites")
sites_dir.mkdir(parents=True, exist_ok=True)
apps_file = sites_dir / "apps.txt"
required_apps = ["frappe", "erpnext", "crm"]
existing = []
if apps_file.exists():
    existing = [line.strip() for line in apps_file.read_text().splitlines() if line.strip()]
apps = existing[:]
for app in required_apps:
    if app not in apps:
        apps.append(app)
apps_file.write_text("\n".join(apps) + "\n")

common_file = sites_dir / "common_site_config.json"
config = {}
if common_file.exists():
    try:
        config = json.loads(common_file.read_text())
    except ValueError:
        config = {}
config.update({
    "db_host": "mariadb",
    "db_port": 3306,
    "redis_cache": "redis://redis:6379/1",
    "redis_queue": "redis://redis:6379/2",
    "redis_socketio": "redis://redis:6379/3",
    "socketio_port": 9000,
})
common_file.write_text(json.dumps(config, indent=2) + "\n")

print("--- sites/apps.txt ---")
print(apps_file.read_text().strip())
print("--- sites/common_site_config.json ---")
print(common_file.read_text().strip())
EOF

RUN chown frappe:frappe /home/frappe/frappe-bench/configurator.py && chmod 755 /home/frappe/frappe-bench/configurator.py

USER frappe

RUN cd /home/frappe/frappe-bench && ./env/bin/pip install -e ./apps/crm