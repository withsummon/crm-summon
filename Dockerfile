FROM frappe/bench:latest AS frontend-builder

USER root
WORKDIR /build/crm

COPY . .

RUN chown -R frappe:frappe /build/crm

USER frappe
WORKDIR /build/crm/frontend

RUN yarn install --frozen-lockfile
RUN yarn build


FROM frappe/erpnext-worker:latest AS worker

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

# Install missing socketio runtime deps
RUN cd /home/frappe/frappe-bench/apps/frappe && \
    cat > package.json <<'PKGJSON' && \
{
  "name": "frappe-socketio-deps",
  "version": "1.0.0",
  "dependencies": {
    "cookie": "*",
    "ioredis": "*",
    "socket.io": "*"
  }
}
PKGJSON
    npm install --no-save && \
    chown -R frappe:frappe node_modules package.json

USER frappe

RUN cd /home/frappe/frappe-bench \
    && echo "=== apps/crm content ===" \
    && ls -la ./apps/crm \
    && test -f ./apps/crm/pyproject.toml \
    && ./env/bin/pip install -e ./apps/crm \
    && node --version \
    && npm --version \
    && test -d ./apps/frappe/node_modules/cookie \
    && test -d ./apps/frappe/node_modules/ioredis \
    && test -d ./apps/frappe/node_modules/socket.io


FROM frappe/erpnext-nginx:latest AS nginx

USER root

COPY --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm