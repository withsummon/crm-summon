# Stage 1: Build the frontend (Vue 3 / Vite)
FROM node:18-bookworm-slim AS frontend-builder
WORKDIR /build

# Copy the entire repository to ensure all workspace dependencies (like frappe-ui) are present
COPY . .

# Run yarn install and build in the frontend directory
WORKDIR /build/frontend
RUN yarn install --frozen-lockfile && yarn build

# Stage 2: Build the Frappe Image
FROM frappe/erpnext:version-15
USER root

# Create the apps directory for our custom app
RUN mkdir -p /home/frappe/frappe-bench/apps/crm

# Copy the custom app along with the built frontend assets from Stage 1
COPY --chown=frappe:frappe --from=frontend-builder /build/crm /home/frappe/frappe-bench/apps/crm/

USER frappe

# Install the app into the python environment and register it in apps.txt
RUN cd /home/frappe/frappe-bench && \
    ./env/bin/pip install -e ./apps/crm && \
    echo "crm" >> ./sites/apps.txt
