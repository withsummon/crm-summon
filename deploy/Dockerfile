FROM frappe/bench:latest AS frontend-builder

USER root

WORKDIR /build/crm

COPY . .

RUN chown -R frappe:frappe /build/crm

USER frappe

WORKDIR /build/crm/frontend

RUN yarn install --frozen-lockfile
RUN yarn build


# --- Worker Stage ---
FROM frappe/erpnext-worker:latest AS worker

USER root

COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm

USER frappe

RUN cd /home/frappe/frappe-bench && \
    echo "=== apps/crm content ===" && \
    ls -la ./apps/crm && \
    test -f ./apps/crm/pyproject.toml && \
    ./env/bin/pip install -e ./apps/crm && \
    grep -qxF "crm" ./sites/apps.txt || echo "crm" >> ./sites/apps.txt


# --- Nginx Stage ---
FROM frappe/erpnext-nginx:latest AS nginx

USER root

# Copy the built app from the worker stage so Nginx has access to the assets
COPY --chown=frappe:frappe --from=worker /home/frappe/frappe-bench/apps/crm /home/frappe/frappe-bench/apps/crm

USER frappe

# Ensure apps.txt is updated for the frontend as well so nginx-entrypoint.sh knows what assets to sync
RUN cd /home/frappe/frappe-bench && \
    grep -qxF "crm" ./sites/apps.txt || echo "crm" >> ./sites/apps.txt