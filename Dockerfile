# --- Frontend Builder Stage ---
FROM frappe/bench:latest AS frontend-builder

USER root

WORKDIR /build/crm

COPY . .

RUN chown -R frappe:frappe /build/crm

USER frappe

WORKDIR /build/crm/frontend

RUN yarn install --frozen-lockfile
RUN yarn build


# --- Worker Image ---
FROM frappe/erpnext-worker:latest AS worker

USER root

# Required for websocket service:
# node /home/frappe/frappe-bench/apps/frappe/socketio.js
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

USER frappe

# Install custom CRM app into Frappe virtualenv.
# Do NOT write to sites/apps.txt here because runtime Docker volume overrides /sites.
# Do NOT run yarn install inside apps/frappe; base image already has its own dependencies.
RUN cd /home/frappe/frappe-bench \
    && echo "=== apps/crm content ===" \
    && ls -la ./apps/crm \
    && test -f ./apps/crm/pyproject.toml \
    && ./env/bin/pip install -e ./apps/crm \
    && node --version \
    && npm --version


# --- Nginx Image ---
FROM frappe/erpnext-nginx:latest AS nginx

USER root

COPY --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm

USER frappe