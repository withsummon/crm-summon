# Production-grade Frappe Docker Deployment

This folder contains a production-ready Docker deployment architecture for Frappe Framework v15 using official `frappe_docker` conventions and immutable images.

## Architecture Overview

- Immutable container images built from `docker/Dockerfile`
- App installation driven by `apps.json` during image build
- Multi-service topology with clear service separation:
  - `backend`
  - `socketio`
  - `scheduler`
  - `worker`
  - `redis-cache`
  - `redis-queue`
  - `redis-socketio`
  - `mariadb`
  - `nginx`
- Persistent volumes for data and site state
- CI/CD-friendly build and deploy workflow
- No manual `bench get-app` or install operations in running containers

## Folder Structure

```
/docker
  ├── Dockerfile
  ├── docker-compose.prod.yml
  ├── .env.example
  ├── nginx/
  │   └── conf.d/
  │       └── frappe.conf
  └── README.md
.github/
  └── workflows/
      └── frappe-ci-cd.yml
apps.json
```

## apps.json Examples

### A. Example with ERPNext

```json
[
  { "url": "https://github.com/frappe/frappe.git", "branch": "version-15" },
  { "url": "https://github.com/frappe/erpnext.git", "branch": "version-15" },
  { "url": "https://github.com/withsummon/crm-summon.git", "branch": "develop" }
]
```

### B. Example without ERPNext

```json
[
  { "url": "https://github.com/frappe/frappe.git", "branch": "version-15" },
  { "url": "https://github.com/withsummon/crm-summon.git", "branch": "develop" }
]
```

### C. Private Git repository with PAT/token

```json
[
  { "url": "https://github.com/frappe/frappe.git", "branch": "version-15" },
  { "url": "https://github.com/your-org/private-app.git", "branch": "main" },
  { "url": "https://github.com/withsummon/crm-summon.git", "branch": "develop" }
]
```

> Use Docker BuildKit and `--secret id=git_token,src=git_token.txt` to safely inject the PAT at build time. Do not commit the token to source control.

### D. Public GitHub repository example

```json
[
  { "url": "https://github.com/frappe/frappe.git", "branch": "version-15" },
  { "url": "https://github.com/withsummon/crm-summon.git", "branch": "develop" }
]
```

## Build and Tagging Strategy

### Build command

```bash
DOCKER_BUILDKIT=1 docker build \
  --secret id=git_token,src=git_token.txt \
  --build-arg FRAPPE_VERSION=version-15 \
  --build-arg APPS_JSON=apps.json \
  -f docker/Dockerfile \
  -t registry.example.com/your-org/crm-summon:staging \
  .
```

### Tag strategy

- `registry.example.com/your-org/crm-summon:staging`
- `registry.example.com/your-org/crm-summon:production`
- `registry.example.com/your-org/crm-summon:${GITHUB_SHA}`

### Rollback strategy

- Keep image digests in the registry
- Deploy a previous digest or tag with `docker compose pull` and `docker compose up -d`
- If a release fails, rollback by replacing `${FRAPPE_IMAGE}` in `.env` to a known-good tag

## Docker Compose Production Architecture

The Compose stack is defined in `docker/docker-compose.prod.yml` and separates:

- application runtime (`backend`)
- job scheduling (`scheduler`)
- queued workers (`worker`)
- realtime socket handling (`socketio`)
- stateful services (`mariadb`, `redis-*`)
- edge proxy (`nginx`)

It uses volumes for durability and healthchecks for container readiness.

## CI/CD Pipeline

The GitHub Actions workflow at `.github/workflows/frappe-ci-cd.yml` performs:

1. checkout code
2. build immutable Docker image
3. push image to registry
4. deploy to remote server via SSH
5. execute migrations and cache refresh

### Secrets required

- `REGISTRY_URL`
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`
- `GIT_TOKEN_FILE_PATH`
- `DEPLOY_HOST`
- `DEPLOY_USER`
- `DEPLOY_PORT`
- `DEPLOY_PATH`
- `DEPLOY_SSH_KEY`
- `SITE_NAME`

## Security Best Practices

- Use Docker secrets rather than storing PATs in source control.
- Keep credentials in environment variables outside the repository.
- Use HTTPS and TLS certificates in `docker/nginx/certs`.
- Use `nginx:stable-alpine` for hardened proxy behavior.
- Apply least privilege by running Frappe containers as the `frappe` user.
- Restrict database access to the Docker network only.
- Use `restart: unless-stopped` and healthchecks to recover from transient failures.

## Production Best Practices

- Immutable infrastructure means: build once, deploy many, never modify the container in place.
- Avoid `bench get-app` or `bench install-app` in running containers; these are development anti-patterns.
- Scale workers with `docker compose up -d --scale worker=3` when queue load increases.
- Use separate Redis instances for cache, queue, and socketio.
- Keep MariaDB data on a dedicated volume and back it up regularly.

## Deployment Flow

1. Developer push to GitHub
2. CI builds immutable image and tags it
3. Registry stores versioned image
4. Production server pulls the image
5. `docker compose up -d --remove-orphans` performs a rolling update

## Troubleshooting

- App install failures: verify `apps.json`, Git branch names, and private repo access.
- Redis connection issues: confirm service names match `REDIS_*` env vars and healthchecks.
- Websocket failures: verify `nginx` proxy headers and `socketio` service reachability.
- Migration issues: use `docker compose exec backend bench --site ${SITE_NAME} migrate`.
- Permission problems: ensure volumes are owned by `frappe:frappe` and not root.
- Volume corruption: restore from snapshot or backup rather than deleting live data.
- Container restart loops: inspect `docker compose logs --tail 100` and validate `healthcheck` commands.
- MariaDB readiness issues: ensure `mariadb` service is healthy before backend startup.

## Infrastructure Recommendations

- Small scale: single host, 4 CPU / 16 GB RAM, dedicated SSD, moderate traffic.
- Medium scale: 2-3 hosts, 8 CPU / 32 GB RAM, separate DB host, load-balanced web and worker nodes.
- Enterprise: deploy on Kubernetes or managed container platform; separate database cluster, Redis cluster, object storage, and autoscaling workers.
- Docker Compose vs Kubernetes:
  - Compose: best for small-to-medium deployments, simple management, fast setup.
  - Kubernetes: best for enterprise demand, autoscaling, service discovery, and multi-availability-zone resilience.

## Notes

This production-ready design is intentionally reproducible via code and avoids manual container edits or runtime app installs.
