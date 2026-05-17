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

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

# Fix Frappe socketio dependencies
RUN rm -rf /home/frappe/frappe-bench/apps/frappe/node_modules && \
    chown -R frappe:frappe /home/frappe/frappe-bench/apps/frappe

USER frappe

RUN cd /home/frappe/frappe-bench && \
    echo "=== apps/crm content ===" && \
    ls -la ./apps/crm && \
    test -f ./apps/crm/pyproject.toml && \
    ./env/bin/pip install -e ./apps/crm && \
    grep -qxF "crm" ./sites/apps.txt || echo "crm" >> ./sites/apps.txt

RUN cd /home/frappe/frappe-bench/apps/frappe && \
    yarn install --frozen-lockfile


# --- Nginx Image ---
FROM frappe/erpnext-nginx:latest AS nginx

USER root

COPY --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm

RUN cd /home/frappe/frappe-bench && \
    mkdir -p ./sites && \
    touch ./sites/apps.txt && \
    grep -qxF "crm" ./sites/apps.txt || echo "crm" >> ./sites/apps.txt