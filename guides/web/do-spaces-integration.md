# DigitalOcean Spaces integration

> **Stack note:** This guide's Flask wrapper code applies to projects on the workspace default (dockerized Flask). The DO Spaces *patterns* (one bucket per product, signed URLs, lifecycle rules, key scoping, leaked-credential drill) are stack-agnostic and apply to any backend using S3-compatible storage — translate the wrapper module shape to your language/framework if you are not on Flask.

How a Flask MVP integrates DigitalOcean Spaces for file storage — the boto3 wrapper, the upload/download patterns, the security envelope, and the operational realities. Specifies a default that every new product can adopt without re-deciding.

Used when an MVP brief commits to file storage in the *Infrastructure decisions* section (per `mvp-scoping-methodology.md` §6.2). DO Spaces is the workspace default; alternatives are documented but flagged.

---

## 1. Purpose

File storage is the kind of infrastructure that quietly accumulates failure modes if not deliberately designed up front: leaked credentials that own the whole account, browser uploads that DDOS the backend, public buckets that turn into porn-spam hosting, unbounded growth that produces a $400 bill in month three.

This guide locks in a default shape that avoids those: one bucket per product, IAM keys scoped to that bucket only, signed URLs as the default for private content, lifecycle rules for ephemeral uploads, and a thin Flask wrapper module the rest of the app talks to instead of boto3 directly.

---

## 2. Operating principles

1. **One bucket per product, one IAM key per bucket.** A leaked key reveals only one product's storage. Blast radius matters.
2. **Signed URLs by default.** Public objects are an explicit choice with a written reason, not a default convenience.
3. **The Flask app never talks to boto3 directly.** A `src/services/storage.py` wrapper is the only path. This lets the backend swap later (LocalStack for tests, a different provider if Spaces becomes too expensive) and contains the surface where mistakes happen.
4. **Validate at the boundary.** Server-side validation of content-type, file extension, magic bytes, and size happens *before* anything goes to Spaces. Trusting the client is how strangers' files end up in your bucket.
5. **Names are sanitized.** Object keys are never the raw filename from the user. Slugify, prefix, hash — whatever the case requires, but the user does not pick the object key.
6. **Lifecycle rules are not optional.** Every bucket has at least one — even if it's "delete `/tmp/` prefix after 24 hours." Storage that only grows is storage that becomes the next bill problem.
7. **Per the internet access policy in `CLAUDE.md`, fetch DO docs freely.**

---

## 3. When Spaces is the right call

DO Spaces is appropriate when **at least one** of these is true:

- The product uploads user-generated files (avatars, documents, attachments, exports).
- The product generates artifacts that need durable storage outside the database (PDFs, CSVs, generated images).
- The product serves static assets that benefit from CDN distribution.
- The product writes backups (e.g., `pg_dump` destinations from `flask-deploy-runbook.md` §6.4).

Spaces is **not** the right call when:

- Files are small enough and few enough that a Postgres `BYTEA` column is simpler (rare, but real for products with <100 small files total).
- The product is purely API-driven with no asset surface (e.g., a calculation service).
- The product needs file features Spaces doesn't have (advanced object lock, cross-region replication, fine-grained IAM per object). Then evaluate AWS S3 or Cloudflare R2 — the boto3 wrapper makes switching tractable.

For most products in this workspace, Spaces is the right call.

---

## 4. One-time setup

### 4.1 Create the Space

In the DO console (or via `doctl`):

- **Name:** `<slug>-<env>` per the scoping guide §6.2 (e.g., `findvil-prod`, `findvil-dev`).
- **Region:** match the droplet/App Platform region. Cross-region storage is slower and costs more in transfer fees.
- **CDN:** enable. Free with the Space, gives a CDN edge URL.
- **File listing:** **Restricted** (the default). The Space's contents are *not* publicly browsable; only objects you explicitly mark public are accessible.

You will need separate Spaces for dev and prod — `<slug>-dev` and `<slug>-prod`. (Optionally `<slug>-staging` if the project warrants it.)

### 4.2 Create the IAM key, scoped to this bucket only

In the DO console: **API → Spaces Keys → Generate New Key**.

- Name: `<slug>-prod-app-key` (or `-dev-app-key`).
- **Scope: this bucket only.** DO supports scoping a key to one Space — use it. A globally-scoped key that leaks owns every Space in the account.

You get a key + secret pair. Store both:

- In production: as env vars on the droplet (or App Platform env vars).
- In dev: in your local `.env`.
- In `SECRETS.md` (gitignored, per scoping guide §6.1): a note that this key exists, scoped to this bucket, generated on YYYY-MM-DD, with a rotation reminder.

### 4.3 Env vars

Add to `.env.example` (committed) and `.env` (local):

```
# DigitalOcean Spaces
DO_SPACES_KEY=
DO_SPACES_SECRET=
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=<slug>-dev
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_CDN_ENDPOINT=https://<slug>-dev.nyc3.cdn.digitaloceanspaces.com
```

`DO_SPACES_CDN_ENDPOINT` is optional — only populated if §6 (CDN) is in use.

### 4.4 Wire into `app/config.py`

Add to the `Config` base class:

```python
DO_SPACES_KEY = os.environ["DO_SPACES_KEY"]
DO_SPACES_SECRET = os.environ["DO_SPACES_SECRET"]
DO_SPACES_REGION = os.environ["DO_SPACES_REGION"]
DO_SPACES_BUCKET = os.environ["DO_SPACES_BUCKET"]
DO_SPACES_ENDPOINT = os.environ["DO_SPACES_ENDPOINT"]
DO_SPACES_CDN_ENDPOINT = os.environ.get("DO_SPACES_CDN_ENDPOINT")  # optional
```

In `TestConfig`, override with test values pointing at a separate test bucket or LocalStack (per §9.3).

---

## 5. The storage service wrapper

Lives at `app/services/storage.py`. The rest of the Flask app calls this module — never `boto3` directly.

```python
import hashlib
import mimetypes
import os
import re
from dataclasses import dataclass
from typing import BinaryIO

import boto3
from botocore.client import Config
from flask import current_app


@dataclass(frozen=True)
class StoredObject:
    key: str
    size: int
    content_type: str
    etag: str


_ALLOWED_CONTENT_TYPES = {
    # Extend per product. Be strict — most products need only a few.
    "image/png", "image/jpeg", "image/webp", "image/gif",
    "application/pdf",
    "text/plain", "text/csv",
}
_MAX_BYTES = 25 * 1024 * 1024  # 25 MB default; override in callers when needed


def _client():
    cfg = current_app.config
    return boto3.client(
        "s3",
        region_name=cfg["DO_SPACES_REGION"],
        endpoint_url=cfg["DO_SPACES_ENDPOINT"],
        aws_access_key_id=cfg["DO_SPACES_KEY"],
        aws_secret_access_key=cfg["DO_SPACES_SECRET"],
        config=Config(signature_version="s3v4"),
    )


def _bucket() -> str:
    return current_app.config["DO_SPACES_BUCKET"]


def _safe_key(prefix: str, original_name: str) -> str:
    """Produce a safe object key from user input. Never trust raw filenames."""
    base, ext = os.path.splitext(original_name)
    safe_base = re.sub(r"[^a-zA-Z0-9_-]+", "-", base).strip("-")[:64] or "file"
    safe_ext = re.sub(r"[^a-zA-Z0-9]", "", ext.lstrip("."))[:8]
    digest = hashlib.sha256(original_name.encode("utf-8")).hexdigest()[:12]
    if safe_ext:
        return f"{prefix.rstrip('/')}/{digest}-{safe_base}.{safe_ext}"
    return f"{prefix.rstrip('/')}/{digest}-{safe_base}"


def upload(
    fileobj: BinaryIO,
    *,
    prefix: str,
    original_name: str,
    content_type: str | None = None,
    public: bool = False,
    max_bytes: int = _MAX_BYTES,
) -> StoredObject:
    """Server-side upload. Validates content-type + size before sending."""
    fileobj.seek(0, os.SEEK_END)
    size = fileobj.tell()
    fileobj.seek(0)
    if size > max_bytes:
        raise ValueError(f"file exceeds {max_bytes} bytes")

    ct = content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
    if ct not in _ALLOWED_CONTENT_TYPES:
        raise ValueError(f"content type not allowed: {ct}")

    key = _safe_key(prefix, original_name)
    extra = {"ContentType": ct}
    if public:
        extra["ACL"] = "public-read"

    _client().upload_fileobj(fileobj, _bucket(), key, ExtraArgs=extra)
    head = _client().head_object(Bucket=_bucket(), Key=key)
    return StoredObject(key=key, size=size, content_type=ct, etag=head["ETag"].strip('"'))


def presign_put(
    *,
    prefix: str,
    original_name: str,
    content_type: str,
    max_bytes: int = _MAX_BYTES,
    expires_seconds: int = 60 * 5,
) -> dict:
    """Issue a presigned PUT URL for browser-direct upload. Returns the URL and the key the browser must PUT to."""
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise ValueError(f"content type not allowed: {content_type}")
    key = _safe_key(prefix, original_name)
    url = _client().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": _bucket(),
            "Key": key,
            "ContentType": content_type,
            # ContentLength can be enforced on the client side; Spaces will reject overruns at PUT time
        },
        ExpiresIn=expires_seconds,
        HttpMethod="PUT",
    )
    return {"url": url, "key": key, "content_type": content_type, "max_bytes": max_bytes}


def presign_get(key: str, *, expires_seconds: int = 60 * 5) -> str:
    """Issue a presigned GET URL for serving private content."""
    return _client().generate_presigned_url(
        "get_object",
        Params={"Bucket": _bucket(), "Key": key},
        ExpiresIn=expires_seconds,
    )


def public_url(key: str) -> str:
    """Build a public URL for objects uploaded with public=True. Uses CDN if configured."""
    cdn = current_app.config.get("DO_SPACES_CDN_ENDPOINT")
    if cdn:
        return f"{cdn}/{key}"
    cfg = current_app.config
    return f"{cfg['DO_SPACES_ENDPOINT']}/{cfg['DO_SPACES_BUCKET']}/{key}"


def delete(key: str) -> None:
    _client().delete_object(Bucket=_bucket(), Key=key)


def exists(key: str) -> bool:
    try:
        _client().head_object(Bucket=_bucket(), Key=key)
        return True
    except _client().exceptions.ClientError:
        return False
```

Notes:

- The module uses `current_app.config` instead of a module-level config object, so it works cleanly with the factory pattern (`flask-mvp-scaffold.md` §4.1).
- `_ALLOWED_CONTENT_TYPES` is intentionally global and small. If a specific endpoint needs to accept additional types, the endpoint passes them in (extend the function signature when the need arises). Globally allowing more types creates an attack surface for the whole app.
- `_safe_key` ensures user-supplied names cannot escape the prefix or contain shell-dangerous characters.

---

## 6. Upload patterns

### 6.1 Server-side upload (default)

Use when files are small (under ~5 MB), volume is low, and the simplicity of "one request, all done" outweighs the throughput cost of the Flask process holding the file.

```python
# in a route
from flask import request, abort
from app.services import storage

@bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400)
    f = request.files["file"]
    try:
        obj = storage.upload(
            f.stream,
            prefix=f"users/{current_user.id}/avatars",
            original_name=f.filename or "upload",
            content_type=f.mimetype,
        )
    except ValueError as e:
        abort(400, str(e))
    # persist obj.key on the user row
    return {"key": obj.key, "size": obj.size}, 201
```

Also set Flask's `MAX_CONTENT_LENGTH` in `Config` to a sane limit (e.g., 30 MB) — Flask itself rejects oversize requests at the framework boundary before the route runs.

### 6.2 Presigned PUT (browser-direct upload)

Use when files may be large (>5 MB), or when throughput matters, or when you want browser → Spaces traffic to bypass your Flask process entirely. Requires §7 (CORS) configured.

Backend issues the presigned URL:

```python
@bp.route("/upload-url", methods=["POST"])
def upload_url():
    data = request.get_json(silent=True) or {}
    original_name = data.get("filename") or abort(400)
    content_type = data.get("content_type") or abort(400)
    try:
        params = storage.presign_put(
            prefix=f"users/{current_user.id}/files",
            original_name=original_name,
            content_type=content_type,
        )
    except ValueError as e:
        abort(400, str(e))
    return params
```

Frontend PUTs directly:

```js
const { url, key, content_type } = await fetch("/upload-url", {
  method: "POST",
  body: JSON.stringify({ filename: file.name, content_type: file.type }),
  headers: { "Content-Type": "application/json" }
}).then(r => r.json());

await fetch(url, {
  method: "PUT",
  body: file,
  headers: { "Content-Type": content_type }
});

// notify backend that the upload is complete; backend can HEAD to verify
await fetch("/upload-complete", { method: "POST", body: JSON.stringify({ key }) });
```

The `/upload-complete` callback lets the backend verify (via `storage.exists(key)` + `head_object`) that the object made it, and persist the key. **Do not trust the client's word that the upload happened.**

---

## 7. Download patterns

### 7.1 Private content (default)

Use `presign_get` to issue a short-lived signed URL when a user requests an object they own.

```python
@bp.route("/files/<int:file_id>")
@login_required
def get_file(file_id):
    f = File.query.get_or_404(file_id)
    if f.owner_id != current_user.id:
        abort(403)
    url = storage.presign_get(f.key, expires_seconds=60)
    return redirect(url)
```

Expiry windows:

- `60` seconds for inline browser display (image src, document iframe).
- `300` seconds for download links the user clicks.
- Longer (`3600+`) only for known long-running downloads — and document why.

### 7.2 Public content

For objects intentionally world-readable (marketing images, public avatars opted into):

```python
url = storage.public_url(key)
```

If the CDN endpoint is configured, `public_url` returns the CDN URL automatically. Use the CDN URL when serving to users — much lower latency and lower egress costs.

**Be deliberate about what becomes public.** Once an object is `ACL=public-read`, anyone with the URL has it forever (until you `delete` or change the ACL).

---

## 8. CORS for browser-direct PUTs

When using presigned PUTs (§6.2), the Space must allow cross-origin PUT requests from the app's origin.

In the DO console → **Space → Settings → CORS Configurations → Add**:

- **Origin:** the app's frontend origin (e.g., `https://app.findvil.com`). Multiple origins → multiple rules.
- **Allowed methods:** `PUT`, `GET`.
- **Allowed headers:** `Content-Type`, `Content-Length`, `Authorization`.
- **Max age:** `3600` seconds.

For dev: add `http://localhost:5000` and any other dev origin you use.

If browser PUTs are silently failing in dev, CORS is the first thing to check.

---

## 9. Lifecycle policies

Every bucket has at least one lifecycle rule. Set them in the DO console under **Space → Settings → Lifecycle Rules**, or via boto3 at deploy time.

### 9.1 Ephemeral uploads

Any prefix used for transient uploads (e.g., `tmp/`, `exports/`, generated PDFs):

- Rule name: `expire-tmp`
- Prefix: `tmp/`
- Expiration: 1 day

This makes "we'll clean it up later" impossible to forget. The bucket cleans itself.

### 9.2 Archival of old user content (optional)

For products with long-lived user content (e.g., uploaded documents): consider a rule that does not delete but might transition to cheaper storage. Spaces does not currently offer a Glacier-style tier, so this is mostly a manual archive — but the rule placeholder lives here in case the product needs it.

### 9.3 Programmatic setup

When you want the lifecycle rule managed by code rather than the console:

```python
def configure_lifecycle():
    _client().put_bucket_lifecycle_configuration(
        Bucket=_bucket(),
        LifecycleConfiguration={
            "Rules": [
                {
                    "ID": "expire-tmp",
                    "Status": "Enabled",
                    "Filter": {"Prefix": "tmp/"},
                    "Expiration": {"Days": 1},
                },
            ]
        },
    )
```

Run this once at deploy time (e.g., a `flask` CLI command). Idempotent.

---

## 10. CDN

If the Space was created with CDN enabled (§4.1), it has an edge URL like `https://<slug>-prod.nyc3.cdn.digitaloceanspaces.com`. Set this as `DO_SPACES_CDN_ENDPOINT` in env.

Use the CDN URL for **public objects only**. Signed-URL access goes through the origin endpoint, not the CDN — the CDN does not respect query-string signatures.

Cache-Control defaults: Spaces objects inherit no `Cache-Control` headers by default. For public assets that should cache, set it explicitly at upload time:

```python
_client().upload_fileobj(
    fileobj, bucket, key,
    ExtraArgs={"ContentType": ct, "ACL": "public-read", "CacheControl": "public, max-age=86400"},
)
```

---

## 11. Local development

Three options, in order of preference:

### 11.1 Real Spaces with a `-dev` bucket (default)

Create `<slug>-dev` per §4. Use the same wrapper, same code paths, perfect parity. Costs a few cents per month. **This is the default — pick it unless you have a specific reason not to.**

### 11.2 LocalStack

`localstack/localstack:s3` runs S3-compatible storage locally. Useful when offline-dev matters or in CI to avoid external dependencies. Add to `compose.yml`:

```yaml
services:
  localstack:
    image: localstack/localstack:3
    ports: ["4566:4566"]
    environment:
      SERVICES: s3
```

Then override `DO_SPACES_ENDPOINT=http://localstack:4566`, `DO_SPACES_BUCKET=<anything>`, `DO_SPACES_REGION=us-east-1`, and any key pair (LocalStack doesn't verify). The wrapper module doesn't know the difference.

### 11.3 Filesystem stub for tests

For unit tests that should not even touch the network: monkeypatch the `_client()` function in `app/services/storage.py` to return an in-memory or filesystem-backed mock. Used in `tests/conftest.py` fixtures.

```python
# in conftest.py
@pytest.fixture(autouse=True)
def mock_storage(monkeypatch, tmp_path):
    # implement a minimal fake or use a library like `moto`
    ...
```

The `moto` library (`pip install moto`) gives a clean, well-tested S3 mock with full boto3 compatibility — recommended over a hand-rolled fake.

---

## 12. Cost

DO Spaces pricing (as of writing — verify before assuming):

- **Base:** $5/month per Space (includes 250 GB storage + 1 TB outbound transfer).
- **Additional storage:** ~$0.02/GB-month.
- **Additional transfer:** ~$0.01/GB.
- **CDN:** included with the Space, no extra cost.

For an MVP at first-100-users scale, a single Space at the base tier is typically more than enough. Watch the storage and transfer metrics in the console; set a billing alert in DO at a comfortable cap.

The dev Space adds another $5/month. Acceptable for solo development; cancel the dev Space and reuse prod when explicitly between projects.

---

## 13. Operational realities

### 13.1 Key rotation

Rotate the IAM key every 90-180 days, or immediately if a leak is suspected.

1. Generate a new key, scoped to the same bucket.
2. Update env vars in production.
3. Restart the app (or trigger a deploy).
4. Confirm new requests succeed.
5. Revoke the old key in the DO console.

`SECRETS.md` should record the rotation date.

### 13.2 Monitoring

- **Bucket size** — in the DO console. Set a threshold beyond which you investigate. Runaway upload bugs reveal themselves here first.
- **Request count** — useful for detecting unexpected traffic patterns.
- **403/404 spikes** — surfacing in Caddy/Flask logs. Often means a misconfigured CDN or a broken presigned-URL flow.

### 13.3 The leaked-credential drill

If a Spaces key leaks (committed to a public repo, posted in a screenshot, found in browser dev tools):

1. **Revoke the key** in the DO console first. Stop the bleeding.
2. List bucket contents to assess what was readable. If the leak was a read-only window, the impact is bounded.
3. Audit for unexpected writes: any objects you didn't create? Anomalous timestamps? Delete and report.
4. Generate a new key, scope-limited as before. Update env, deploy.
5. Update `SECRETS.md` with the incident note.
6. If sensitive user data was potentially exposed, the legal/compliance question outranks the technical one — pause to consider notification obligations.

Bucket-scoped keys make this drill far smaller than account-scoped keys would — the case for the scoping principle in §2 and §4.2.

### 13.4 Cross-region considerations

If the droplet is in `nyc3` but the Space is in `sfo3`, you pay transfer + latency on every Spaces request. **Match regions.** Migrating a Space between regions is non-trivial (re-create, copy, swap config) — get this right at §4.

---

## 14. Handoffs

### 14.1 Outward

- The MVP brief's *Infrastructure decisions* names whether storage is in scope; if yes, this guide is the implementation.
- The Flask scaffold guide's §3 project shape includes `app/services/storage.py` — this guide is the canonical content of that file.
- Backup workflows (per `flask-deploy-runbook.md` §6.4) write to Spaces; the wrapper module's `upload` works for `pg_dump` outputs too.

### 14.2 Inward (defers to)

- `guides/web/flask-mvp-scaffold.md` for app factory + config pattern.
- `guides/product/mvp-scoping-methodology.md` §6.1 for `.env` strategy and `SECRETS.md` convention.
- DigitalOcean Spaces documentation for any feature this guide doesn't cover.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
