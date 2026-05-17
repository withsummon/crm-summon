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

USER frappe

RUN cd /home/frappe/frappe-bench && \
    ls -la ./apps/crm && \
    test -f ./apps/crm/pyproject.toml && \
    ./env/bin/pip install -e ./apps/crm && \
    grep -qxF "crm" ./sites/apps.txt || echo "crm" >> ./sites/apps.txt