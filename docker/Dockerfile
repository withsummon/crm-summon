# syntax=docker/dockerfile:1.4
ARG FRAPPE_VERSION=version-15
ARG APPS_JSON=apps.json
ARG BASE_IMAGE=frappe/erpnext-worker:${FRAPPE_VERSION}

FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.source="https://github.com/withsummon/crm-summon"
LABEL org.opencontainers.image.version="${FRAPPE_VERSION}"
LABEL org.opencontainers.image.vendor="Summon CRM"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"

USER root
WORKDIR /home/frappe/frappe-bench

COPY ${APPS_JSON} /tmp/apps.json

RUN mkdir -p /home/frappe/frappe-bench \
    && chown -R frappe:frappe /home/frappe /tmp/apps.json

USER frappe

RUN --mount=type=secret,id=git_token \
    if [ -s /run/secrets/git_token ]; then \
      git config --global url."https://x-access-token:$(cat /run/secrets/git_token)@github.com/".insteadOf "https://github.com/"; \
    fi && \
    bench init /home/frappe/frappe-bench \
      --frappe-branch ${FRAPPE_VERSION} \
      --skip-redis-config-generation \
      --apps_path /tmp/apps.json

EXPOSE 8000 9000

ENTRYPOINT ["bench"]
CMD ["serve", "--port", "8000", "--socketio_port", "9000"]
