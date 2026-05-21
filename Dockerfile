FROM frappe/bench:latest AS frontend-builder

USER root
WORKDIR /build/crm

COPY . .

RUN chown -R frappe:frappe /build/crm

USER frappe
WORKDIR /build/crm/frontend

RUN yarn install --frozen-lockfile
RUN yarn build


FROM frappe/erpnext-worker:version-15 AS worker

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

# Install missing socketio runtime deps
RUN cd /home/frappe/frappe-bench/apps/frappe && \
    npm install --no-save cookie@0.4.2 redis@3.1.2 socket.io@2.5.0 && \
    chown -R frappe:frappe node_modules

USER frappe

RUN cd /home/frappe/frappe-bench \
    && echo "=== apps/crm content ===" \
    && ls -la ./apps/crm \
    && test -f ./apps/crm/pyproject.toml \
    && ./env/bin/pip install -e ./apps/crm \
    && node --version \
    && npm --version \
    && cd /home/frappe/frappe-bench/apps/frappe \
    && node -e "require('cookie'); console.log('cookie ok')"


FROM frappe/erpnext-nginx:version-15 AS nginx

USER root

COPY --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm