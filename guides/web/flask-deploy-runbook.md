# Flask deploy runbook

> **Stack note:** Applies to projects using the workspace default of dockerized Flask (per `guides/product/mvp-scoping-methodology.md` §6.0). For other web stacks, the deploy story differs — adapt the principles (target choice, HTTPS, recurring-deploy machinery, migrations, rollback, logs, backups, monitoring) to your stack's idioms.

The operational path from `scaffold-done` (per `flask-mvp-scaffold.md`) to a **live, HTTPS-served, production URL**. Covers the two DigitalOcean targets the scoping guide commits to — droplet + `docker compose` vs. DO App Platform — and the recurring-deploy machinery for both.

This is a *runbook*, not a methodology. It lists the commands and the order. Each section is something you should be able to follow when you have not deployed in three months and have forgotten the details.

---

## 1. Purpose

The Flask scaffold ends at "first deploy works." It does not say *how* the droplet was provisioned, how DNS got pointed, how HTTPS got terminated, or how the next deploy happens without re-doing all of that. This runbook fills those gaps.

A complete first deploy means:

- A reachable IP or hostname under HTTPS.
- A real domain pointing at it (not an `.ondigitalocean.app` placeholder for prod, though that is fine during the first 48 hours).
- The deploy command from `scripts/deploy.sh` works end-to-end.
- Logs are visible to the founder.
- Restart and rollback procedures are known.

---

## 2. Operating principles

1. **Boring tech for ops.** No Kubernetes, no service mesh, no custom orchestration. `docker compose up -d` on a droplet, or DO App Platform's managed runtime. Both proven, both small.
2. **Caddy for HTTPS by default.** Caddy automates Let's Encrypt without configuration. nginx + certbot is a fine alternative but is *more* work for the same outcome on a solo MVP. Pick nginx only when routing complexity actually demands it.
3. **Treat the deploy command as code.** `scripts/deploy.sh` lives in the repo. It is the only sanctioned way to deploy. Manual SSH-and-edit on the production droplet is forbidden — it makes the next session's deploy break in surprising ways.
4. **Logs go to stdout; the platform forwards.** Flask logs to stdout (per `flask-mvp-scaffold.md` §4.5); `docker compose` forwards container logs; DO captures them. No special log forwarder until the project actively needs structured search at volume.
5. **Per the internet access policy in `CLAUDE.md`, fetch DO docs freely** — feature changes happen.

---

## 3. Picking the target

The MVP brief has already chosen one of two targets (per `mvp-scoping-methodology.md` §6.3). This runbook covers both. Briefly:

| | **DO droplet + `docker compose`** | **DO App Platform** |
|---|---|---|
| Setup time | 30-60 min the first time | 10-20 min the first time |
| Recurring deploys | `scripts/deploy.sh` (SSH + `docker compose pull && up -d`) | `git push` to the linked branch *or* `doctl apps create-deployment` |
| Background workers | Trivial (add a service to compose) | Limited; needs a separate "worker" component |
| Websockets / long-lived connections | Native | Constrained |
| Cost (first MVP) | ~$6-12/month droplet + $6/month DB | ~$5-12/month app + $7-15/month managed DB |
| HTTPS | Caddy on the droplet (this runbook) | Native, auto-renewing |
| When to pick | Default for projects that may need background workers, custom routing, exotic networking | Default for stateless web services that fit App Platform's runtime cleanly |

Below: §4 covers the droplet path end-to-end. §5 covers App Platform.

---

## 4. DO droplet runbook

The full sequence from a fresh DO account to a deployed, HTTPS-served MVP.

### 4.1 Provision the droplet

Via the DO console or `doctl`:

- **Size:** start at the smallest regular droplet that meets memory needs. For a Flask MVP with one Postgres, `s-1vcpu-2gb` is usually enough (~$12/month). Step down to `s-1vcpu-1gb` (~$6/month) only after measuring memory in dev.
- **Region:** closest to expected users. Match this with the DO Spaces region (per `do-spaces-integration.md`) when storage is in scope.
- **Image:** Ubuntu LTS (current LTS at provisioning time).
- **SSH key:** add your existing public key during provisioning. Do not pick password auth.
- **Hostname:** `<slug>-prod`.
- **Tags:** `<slug>`, `prod` — useful later when you have multiple droplets.

Note the public IPv4 once it's running.

### 4.2 Initial server hardening (one-time)

SSH in as root, then:

```bash
# Create a deploy user
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Disable root SSH and password auth
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart ssh

# Firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# System updates
apt update && apt upgrade -y
apt install -y fail2ban
systemctl enable --now fail2ban
```

Log out, then verify you can SSH in as `deploy` (not root):

```bash
ssh deploy@<droplet-ip>
```

If that works, root SSH is sealed correctly.

### 4.3 Install Docker

As `deploy`:

```bash
# Docker per https://docs.docker.com/engine/install/ubuntu/
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker deploy
# Log out and back in for the group change to take effect.

# Verify
docker --version
docker compose version
```

### 4.4 Lay down the project directory

```bash
sudo mkdir -p /srv/<slug>
sudo chown deploy:deploy /srv/<slug>
cd /srv/<slug>
git clone <your-repo-url> .
```

For a private repo, prefer deploy keys (`ssh-keygen` on the droplet, paste the public key into the repo's deploy-keys settings) over personal access tokens.

Create `.env` in `/srv/<slug>` on the droplet — production values, not the dev ones. **Never commit production `.env`.** Track the keys it needs in `.env.example` and document where each value comes from in `SECRETS.md` (locally only).

### 4.5 Add Caddy for HTTPS

Caddy terminates HTTPS in front of the Flask container. It handles certificate provisioning and renewal automatically via Let's Encrypt.

Create `Caddyfile` at the project root (committed to the repo):

```
{$DOMAIN} {
    reverse_proxy web:5000
    encode gzip
    log {
        output stdout
        format console
    }
}
```

Extend `compose.prod.yml` with a Caddy service:

```yaml
services:
  web:
    build: .
    env_file: .env
    restart: unless-stopped
    expose: ["5000"]
    depends_on: [db]
  caddy:
    image: caddy:2-alpine
    restart: unless-stopped
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    environment:
      DOMAIN: ${DOMAIN}
    depends_on: [web]
  db:
    image: postgres:16-alpine
    env_file: .env
    restart: unless-stopped
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
  caddy_data:
  caddy_config:
```

`DOMAIN` lives in the droplet's `.env` (e.g., `DOMAIN=app.findvil.com`). Caddy reads it via `${DOMAIN}` substitution.

### 4.6 DNS

In your DNS provider (DO's, or Cloudflare, or wherever the domain lives):

- **A record:** `app.<your-domain>` → droplet IPv4.
- Optional: **AAAA record** if the droplet has IPv6 enabled.
- Wait for propagation (usually under 5 minutes; can be up to an hour).

Verify with `dig app.<your-domain>` from your local machine.

### 4.7 First deploy

On the droplet:

```bash
cd /srv/<slug>
docker compose -f compose.prod.yml up -d --build
```

Watch the Caddy logs come up — it will request a Let's Encrypt cert on first start. Look for "certificate obtained successfully."

```bash
docker compose -f compose.prod.yml logs -f caddy
docker compose -f compose.prod.yml logs -f web
```

From your local machine:

```bash
curl https://app.<your-domain>/healthz
# expect {"status": "ok"}
```

If you get this, the first deploy works.

### 4.8 The repeatable deploy command

Replace the placeholder `scripts/deploy.sh` (per scaffold §5 step 8) with the real one. Commit it.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${DEPLOY_HOST:?Set DEPLOY_HOST=deploy@<droplet-ip-or-domain>}"
: "${DEPLOY_PATH:?Set DEPLOY_PATH=/srv/<slug>}"

ssh "$DEPLOY_HOST" bash -s <<EOF
set -euo pipefail
cd "$DEPLOY_PATH"
git pull --ff-only
docker compose -f compose.prod.yml build --pull
docker compose -f compose.prod.yml up -d
docker compose -f compose.prod.yml ps
EOF

echo "Health check:"
curl -fsS "https://app.<your-domain>/healthz"
echo
echo "Deploy complete."
```

The locals (or a `.env` for deploy-side config) provide `DEPLOY_HOST` and `DEPLOY_PATH`. From your laptop:

```bash
DEPLOY_HOST=deploy@<droplet-ip> DEPLOY_PATH=/srv/<slug> ./scripts/deploy.sh
```

### 4.9 Rolling back

When a deploy breaks production:

```bash
ssh "$DEPLOY_HOST"
cd /srv/<slug>
git log --oneline -5         # find the last good commit
git checkout <good-sha>
docker compose -f compose.prod.yml up -d --build
```

For a faster rollback, tag deploys: each green deploy gets `git tag deploy-YYYYMMDD-HHMM` from `scripts/deploy.sh`. Rollback becomes `git checkout deploy-<previous>`.

### 4.10 Migrations

If using `flask-migrate`:

- Generate migrations locally during development (`flask db migrate -m '...'`) and **commit them**.
- Apply migrations during deploy. Add a one-shot step to `deploy.sh`:

```bash
docker compose -f compose.prod.yml run --rm web flask db upgrade
```

Place this **before** `up -d` so the schema is migrated before the new app starts serving traffic.

For destructive migrations (drop column, rename), do a two-deploy dance: deploy code that tolerates both schemas → run the migration → deploy code that requires the new schema. This is the only reliable solo-deploy pattern when you cannot afford downtime.

---

## 5. DO App Platform runbook

For briefs that picked App Platform per scoping §6.3.

### 5.1 Prepare the repo for App Platform

App Platform reads its config from one of:

- **`.do/app.yaml`** in the repo (recommended — config as code).
- DO console UI (works but loses the as-code benefit).

Minimal `.do/app.yaml` for a Flask app + managed Postgres:

```yaml
name: <slug>
region: nyc
services:
  - name: web
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: <user>/<repo>
      branch: main
      deploy_on_push: true
    http_port: 5000
    routes:
      - path: /
    instance_size_slug: basic-xxs
    instance_count: 1
    envs:
      - { key: FLASK_ENV, value: production }
      - { key: SECRET_KEY, value: ${SECRET_KEY}, type: SECRET }
      - { key: DATABASE_URL, value: ${db.DATABASE_URL} }
databases:
  - name: db
    engine: PG
    version: "16"
    size: db-s-dev-database
    num_nodes: 1
```

Secrets (anything marked `type: SECRET`) are set via the DO console or `doctl`. Plain env vars live in this file.

### 5.2 First deploy

```bash
doctl apps create --spec .do/app.yaml
```

The first build runs from the latest commit on the configured branch. Watch:

```bash
doctl apps list
doctl apps logs <app-id> --type=deploy   # build logs
doctl apps logs <app-id> --type=run      # runtime logs
```

When build succeeds, App Platform gives the service a placeholder URL like `<slug>-xxxxx.ondigitalocean.app`. Hit `/healthz` on that URL to confirm.

### 5.3 Custom domain + HTTPS

In the DO console (or via `doctl apps update`), add the domain (`app.<your-domain>`). App Platform provides DNS instructions — usually a CNAME pointing at the placeholder hostname. Add it at your DNS provider. App Platform automatically provisions a Let's Encrypt certificate; no further config is needed.

### 5.4 Recurring deploys

If `deploy_on_push: true` is set, every push to the configured branch triggers a deploy. For manual control:

```bash
doctl apps create-deployment <app-id>
```

`scripts/deploy.sh` for App Platform becomes very short:

```bash
#!/usr/bin/env bash
set -euo pipefail
: "${APP_ID:?Set APP_ID to the DO App Platform app id}"
doctl apps create-deployment "$APP_ID" --wait
```

### 5.5 Migrations

App Platform supports pre-deploy jobs (`jobs:` block in `app.yaml`). Add one:

```yaml
jobs:
  - name: migrate
    kind: PRE_DEPLOY
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      repo: <user>/<repo>
      branch: main
    run_command: "flask db upgrade"
    envs:
      - { key: DATABASE_URL, value: ${db.DATABASE_URL} }
```

The migrate job runs before the web service comes up on every deploy.

### 5.6 Rolling back

In the DO console: **Apps → <app> → Activity → previous deployment → Rollback**.
From CLI:

```bash
doctl apps list-deployments <app-id>
doctl apps create-deployment <app-id> --force-rebuild  # rebuild from previous good commit
```

For a true rollback, push the previous good commit to the branch — the deploy will catch up. Tag deploy points the same way as on droplets.

---

## 6. Operational realities

Things that bite even when the runbook is followed.

### 6.1 First-deploy timing

The first Let's Encrypt request can take 30-60 seconds. If the first `curl https://...` returns a TLS error, wait, retry. If Caddy logs show "certificate could not be obtained," the most common causes are:

- DNS has not propagated yet → `dig` from the droplet and from your laptop, compare.
- The droplet firewall is not allowing 80/443 → `sudo ufw status`.
- The domain points at the wrong IP → fix the A record.

### 6.2 Where logs live

| Target | Where |
|---|---|
| Droplet | `docker compose -f compose.prod.yml logs -f <service>` |
| App Platform | `doctl apps logs <app-id> --type=run` or DO console |

For longer retention than the local Docker buffer keeps, configure the DO Logsearch add-on or forward to Papertrail / Better Stack. Skip this until the project has had its first production incident — until then, in-place logs are enough.

### 6.3 Restart procedure

```bash
# Droplet
docker compose -f compose.prod.yml restart web

# App Platform
doctl apps update <app-id> --spec .do/app.yaml  # forces re-evaluation
```

Restarting the DB container is almost never the right move. If the DB needs restarting, something else is wrong; investigate.

### 6.4 Backups

- **Postgres on a droplet:** schedule `pg_dump` to S3-compatible storage (DO Spaces) via cron. Minimal script in `scripts/backup.sh`. Without backups, the first lost-data incident is unrecoverable.
- **Postgres on App Platform managed DB:** DO takes daily backups automatically (verify retention in console). Confirm before relying.

### 6.5 What to monitor

Until first 100 users:

- `/healthz` — UptimeRobot or a similar free monitor pinging every 5 minutes.
- Caddy logs — for unexpected 5xx spikes.
- DO billing alerts — set a monthly cap so a runaway dev loop doesn't bill $400.

Beyond first 100 users, real observability (Sentry for errors, structured logs forwarded, application-level metrics) earns its place. Until then, simpler.

### 6.6 When to switch droplet → App Platform (or vice versa)

- **Droplet → App Platform:** when ops time is eating product time and the app doesn't need anything App Platform forbids. Usually a one-evening migration.
- **App Platform → droplet:** when a must-have requires something App Platform won't host (background workers, websockets at scale, custom networking). Usually a two-evening migration.

---

## 7. Handoffs

### 7.1 Outward

- The Flask scaffold guide's §5 step 8 produces a placeholder `scripts/deploy.sh`; this runbook §4.8 or §5.4 replaces it with the real one.
- The MVP brief's *Infrastructure decisions* section lists the chosen target; this runbook is the canonical implementation of either choice.
- Agent-skills' `shipping-and-launch` skill operates on top of an already-deployable shell; this runbook is what makes the shell deployable.

### 7.2 Inward (defers to)

- DigitalOcean's own documentation for any feature this runbook doesn't cover.
- `guides/web/do-spaces-integration.md` for storage configuration (next guide in the queue).
- `guides/product/mvp-scoping-methodology.md` §6.1 for the `.env` strategy and `SECRETS.md` convention.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
