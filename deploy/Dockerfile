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

# Install Node.js + npm for Frappe websocket.
# The worker base image has Python/Bench, but in your runtime it does not have `node`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

# Ensure ownership is correct.
RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/crm \
    && chown -R frappe:frappe /home/frappe/frappe-bench/sites \
    && chown -R frappe:frappe /home/frappe/frappe-bench/logs

USER frappe

# Install custom CRM app into bench virtualenv.
# Do NOT write to sites/apps.txt here because runtime Docker volume overrides /sites.
RUN cd /home/frappe/frappe-bench \
    && echo "=== apps/crm content ===" \
    && ls -la ./apps/crm \
    && test -f ./apps/crm/pyproject.toml \
    && ./env/bin/pip install -e ./apps/crm

# Install socket.io dependencies safely.
# Do NOT delete the existing Frappe node_modules.
RUN cd /home/frappe/frappe-bench/apps/frappe \
    && yarn install --frozen-lockfile


# --- Nginx Image ---
FROM frappe/erpnext-nginx:latest AS nginx

USER root

COPY --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm

RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/crm

USER frappe