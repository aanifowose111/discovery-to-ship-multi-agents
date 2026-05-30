# Flask auth patterns

> **Stack note:** This guide's code applies to projects on the workspace default (dockerized Flask). The auth *principles* (server-side sessions over signed cookies, Argon2id over bcrypt, single-use hashed tokens, threat-modeled flows, cookie hardening, mandatory MFA backup codes, JWT with refresh rotation for mobile clients, audit logs) are framework-agnostic — translate to your stack's idiomatic libraries if you are not on Flask.

Opinionated auth patterns for dockerized Flask MVPs in this workspace. The default is **server-side sessions with `flask-login` + Argon2 password hashing**. OAuth (Authlib) and JWT (for the React Native client) are the two documented exceptions. Everything else is set up to fail securely by default.

This guide is the "solid security mindset" reference: every section names the threat the pattern defends against, the defaults that hold the line, and the failure mode if you skip it.

---

## 1. Purpose

Auth is the surface most likely to leak data, lock real users out, or invite session hijacking. It is also the surface where "I'll harden it later" turns into an incident. This guide locks defaults that:

- Resist credential-stuffing without exotic tooling.
- Survive a leaked session cookie without surrendering the account.
- Handle password reset, email verification, and account deletion without producing the standard footguns (token re-use, address takeover, orphaned data).
- Pair cleanly with the React Native client's JWT-based access (per `guides/mobile/react-native-mvp-scaffold.md` §4.5-§4.6) without introducing two parallel security models.

---

## 2. Operating principles

1. **Default to server-side sessions.** Stateful sessions backed by Redis or the DB are easier to revoke, easier to audit, and harder to misuse than JWTs. Use JWTs only for the mobile client and only when the trade is intentional (see §11).
2. **Hash with Argon2id, not bcrypt.** Argon2id is the current OWASP recommendation. `argon2-cffi` is the canonical Python binding. Bcrypt is acceptable as a fallback only if Argon2 cannot be installed.
3. **Threat-model each flow.** Every auth flow below lists the threat it defends against. If a flow does not name a threat, it is incomplete.
4. **Tokens are single-use unless they have a reason not to be.** Password reset tokens, email verification tokens, and OAuth state nonces are one-shot. Re-use is an attack class.
5. **Sessions expire.** Idle expiry by default; absolute expiry on top. "Remember me" is a separate, longer-lived, narrowly-scoped second token, not "make the session last forever."
6. **Lock out brute-force, not legitimate users.** Rate-limit by IP + identifier with humane thresholds. CAPTCHAs are a last resort, not a first.
7. **Audit logs are mandatory.** Login success, login failure, password change, MFA enrollment/removal, session revocation — all logged with timestamp, IP, user agent, and outcome.
8. **Per `CLAUDE.md`, web research is free** — verify any library version pinned here is still current.

---

## 3. Default stack

| Concern | Library / pattern |
|---|---|
| Session framework | `flask-login` with server-side session store |
| Session backend | `flask-session` with Redis (prod) or filesystem (dev) — *not* the default signed-cookie sessions |
| Password hashing | `argon2-cffi` (`from argon2 import PasswordHasher`) |
| CSRF protection | `flask-wtf` (FlaskForm) for HTML form posts; for JSON endpoints, a per-request CSRF token via `X-CSRF-Token` header |
| Rate limiting | `flask-limiter` backed by Redis |
| Email | `flask-mail` or a transactional-email service SDK (Postmark, Resend) — used for password reset, email verification, MFA backup codes |
| MFA (optional) | TOTP via `pyotp` |
| OAuth (optional) | `authlib` |
| JWT for mobile client (optional) | `pyjwt` with RS256 signing keys |

Install in `pyproject.toml`. Pin versions; review the pins quarterly.

---

## 4. Password hashing — Argon2id

In `app/services/auth.py` (or wherever auth lives in the project):

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash

# Argon2id is the default for PasswordHasher() since argon2-cffi 18.x.
# Defaults: memory_cost=65536 (64 MB), time_cost=3, parallelism=4.
# These are sane for an MVP. Tune up if hardware allows; never tune down.
_ph = PasswordHasher()


def hash_password(plaintext: str) -> str:
    return _ph.hash(plaintext)


def verify_password(stored_hash: str, plaintext: str) -> tuple[bool, str | None]:
    """
    Returns (ok, new_hash). new_hash is set when the stored hash uses
    older parameters and should be rewritten.
    """
    try:
        _ph.verify(stored_hash, plaintext)
    except (VerifyMismatchError, InvalidHash):
        return False, None
    # Rehash on login if params have been bumped since the hash was created.
    if _ph.check_needs_rehash(stored_hash):
        return True, _ph.hash(plaintext)
    return True, None
```

**Threat:** offline attacks against a leaked password column. Argon2id's memory-hard property makes GPU/ASIC attacks expensive.

**Failure mode if skipped:** a leak of the `users` table with bcrypt-cost-10 (or worse, MD5) hashes is a multi-year offline attack waiting to happen. Already-cracked rainbow tables exist for everything below Argon2.

---

## 5. Session security

### 5.1 Backend: server-side store

Default session storage is a signed cookie that contains the data. For auth, this is the wrong default — sessions cannot be revoked, and an attacker with a copied cookie can use it until expiry.

Use `flask-session` with Redis in prod, filesystem in dev:

```python
# app/extensions.py
from flask_session import Session
sess = Session()
```

```python
# in create_app
app.config["SESSION_TYPE"] = "redis" if app.config["ENV"] == "prod" else "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = redis.from_url(app.config["REDIS_URL"]) if app.config["ENV"] == "prod" else None
sess.init_app(app)
```

Sessions can now be revoked by deleting the key from Redis. On logout, deletion is one call. On password change, all sessions for that user can be revoked by tagging keys by user_id and bulk-deleting.

### 5.2 Cookie settings

`ProdConfig` (per `flask-mvp-scaffold.md` §4.3):

```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = timedelta(hours=12)   # idle expiry
```

`SESSION_COOKIE_SAMESITE = "Strict"` is even safer but breaks cross-site OAuth redirects. `"Lax"` is the right default for most flows.

**Threat defended against:** XSS leaking the cookie (HttpOnly), MITM (Secure), CSRF on top-level navigations (SameSite=Lax).

### 5.3 Absolute session expiry

Idle expiry is set by `PERMANENT_SESSION_LIFETIME`. Add an absolute cap via a custom `before_request`:

```python
ABS_SESSION_LIFETIME = timedelta(days=7)

@app.before_request
def enforce_absolute_session_expiry():
    if not current_user.is_authenticated:
        return
    login_time = session.get("_login_time")
    if login_time is None:
        session["_login_time"] = utcnow().timestamp()
        return
    if utcnow().timestamp() - login_time > ABS_SESSION_LIFETIME.total_seconds():
        logout_user()
        # 401 / redirect to login
```

7 days is a sensible MVP default. Longer needs a "remember me" token (§9), not a longer session.

### 5.4 CSRF

For HTML form POSTs: use `flask-wtf` FlaskForm, which auto-includes a CSRF token.

For JSON endpoints (e.g., from a Jinja-rendered page's fetch calls): expose the CSRF token via a meta tag in `base.html` and have the front-end send it as `X-CSRF-Token`:

```html
<meta name="csrf-token" content="{{ csrf_token() }}">
```

```js
const token = document.querySelector('meta[name="csrf-token"]').content;
fetch("/api/...", { headers: { "X-CSRF-Token": token, "Content-Type": "application/json" }, ... });
```

Verify the header server-side via flask-wtf's `validate_csrf()`.

**For the React Native mobile client**: CSRF does not apply (RN is not a browser, no cookies, no cross-origin attacker). The mobile flow uses JWT (§11) and skips CSRF entirely.

---

## 6. Login flow

```python
# app/blueprints/auth/routes.py
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("auth/login.html", form=form)

    rl_key = f"login:{request.remote_addr}:{form.email.data.lower()}"
    if rate_limiter.is_limited(rl_key):
        log_event("login.rate_limited", email=form.email.data)
        flash("Too many attempts. Try again in a few minutes.", "error")
        return render_template("auth/login.html", form=form), 429

    user = User.query.filter_by(email=form.email.data.lower()).first()
    if user is None:
        # Constant-time response — do not leak which emails are registered
        _ph.verify("$argon2id$v=19$m=65536,t=3,p=4$placeholder$placeholder", "wrong")
        rate_limiter.increment(rl_key)
        log_event("login.failed_unknown_email", email=form.email.data, ip=request.remote_addr)
        flash("Invalid email or password.", "error")
        return render_template("auth/login.html", form=form), 401

    ok, new_hash = verify_password(user.password_hash, form.password.data)
    if not ok:
        rate_limiter.increment(rl_key)
        log_event("login.failed", user_id=user.id, ip=request.remote_addr)
        flash("Invalid email or password.", "error")
        return render_template("auth/login.html", form=form), 401

    if new_hash:
        user.password_hash = new_hash
        db.session.commit()

    if not user.email_verified:
        flash("Verify your email to log in. Check your inbox.", "warning")
        return redirect(url_for("auth.email_verification_required"))

    if user.mfa_enabled:
        session["pre_mfa_user_id"] = user.id
        return redirect(url_for("auth.mfa_challenge"))

    login_user(user, remember=form.remember_me.data and not _remember_me_disallowed(user))
    session["_login_time"] = utcnow().timestamp()
    log_event("login.success", user_id=user.id, ip=request.remote_addr, ua=request.user_agent.string)
    rate_limiter.reset(rl_key)
    return redirect(_safe_next_url(request.args.get("next")))
```

Key choices in this flow:

- **No "no such user" disclosure.** Both unknown email and wrong password return the same error and consume the same time budget (the throw-away verify call against a dummy hash).
- **Rate limiting keys on IP + email**, not just IP (single-IP attackers vs. distributed campaigns).
- **Rehash on login** when params have been bumped — slowly upgrades the hash population without forcing a migration.
- **Email verification is required** to log in. Unverified accounts cannot transact.
- **MFA is checked next**, with a pre-MFA holding token in session (not a logged-in session yet).
- **`_safe_next_url`** sanitizes redirect to prevent open-redirect (whitelist same-host or relative paths).

---

## 7. Password reset

The threat: an attacker who knows a victim's email triggers reset, intercepts the email (account takeover via DNS / mailbox compromise / clever phishing), changes the password, owns the account.

The pattern:

```python
# Token issuance
def issue_reset_token(user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.password_reset_token_hash = hashlib.sha256(token.encode()).hexdigest()
    user.password_reset_expires_at = utcnow() + timedelta(hours=1)
    db.session.commit()
    return token  # send via email; never log
```

Notes:

- **Store the hash, not the token.** A leaked DB row should not yield a valid reset link.
- **1-hour expiry max.** 24h is too long; an inbox sitting unattended is a vulnerability.
- **Single-use.** Clear the fields on successful reset.
- **Generic "we sent an email if the address is registered" message** on the request page — don't enumerate registered emails.
- **Rate-limit reset requests** per email and per IP.
- **Invalidate all sessions on successful reset** (delete all session keys tagged with this user_id from Redis).
- **Send a confirmation email** to the user after a successful reset ("Your password was just changed. If this wasn't you, click here.")

---

## 8. Email verification

The threat: someone signs up with an address they don't control, then "verifies" with a fake account; or, an attacker takes over an account by claiming it was theirs all along.

Pattern:

- Verification token issued at signup, same single-use + hashed-storage rules as the reset token.
- Verification link expires in 24-48 hours; a "resend verification" button on the login page handles the rest.
- Until verified, the user cannot log in or take any meaningful action. The user record exists but is dormant.
- **Email change is a re-verification flow**: changing email sends a verification link to the *new* address and a notification to the *old* address. The new address is not adopted until verified.

---

## 9. "Remember me"

The pattern flask-login ships with (`remember=True`) is fine but worth understanding:

- It issues a separate long-lived signed cookie containing the user id + a remember token.
- The user is auto-logged-in when the session cookie is missing but the remember cookie is valid.
- The remember token should be hashed and stored per-user; revoking the remember cookie on password change is mandatory.

Don't use `remember=True` for elevated-trust operations (admin panels, payment changes). Force re-authentication.

Length: 30 days is a typical maximum. Longer is convenience that costs security.

---

## 10. MFA — TOTP

When required (B2B, financial, anything regulated): TOTP via `pyotp`. Skip MFA for first-MVP consumer products unless the brief specifically requires it.

```python
import pyotp

def enroll_mfa(user: User) -> str:
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    user.mfa_enabled = False  # not enabled until they verify a code
    db.session.commit()
    return secret  # display as QR code via pyotp.TOTP(secret).provisioning_uri(...)

def verify_mfa_code(user: User, code: str) -> bool:
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(code, valid_window=1)  # ±30 seconds for clock skew

def confirm_mfa_enrollment(user: User, code: str):
    if verify_mfa_code(user, code):
        user.mfa_enabled = True
        # Issue 6-8 single-use backup codes; hash them on store
        user.backup_codes = [hashlib.sha256(c.encode()).hexdigest()
                             for c in generate_backup_codes(8)]
        db.session.commit()
```

**Backup codes are mandatory.** Without them, a lost device locks the user out permanently. Backup codes are single-use, hashed on storage, regenerable.

---

## 11. JWT for the mobile client

The React Native client (per `react-native-mvp-scaffold.md` §4.5-§4.6) does not use cookies. It authenticates by POSTing credentials to a token endpoint and receiving a JWT it stores in `expo-secure-store`.

```python
# app/blueprints/api/auth.py
import jwt
from datetime import datetime, timedelta, timezone

JWT_ISSUER = "agents-app"
JWT_AUDIENCE = "agents-mobile"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=30)


def issue_token_pair(user: User) -> dict:
    now = datetime.now(timezone.utc)
    access_payload = {
        "iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "sub": str(user.id),
        "iat": now, "exp": now + ACCESS_TTL,
        "typ": "access",
    }
    refresh_id = secrets.token_urlsafe(24)
    refresh_payload = {
        "iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "sub": str(user.id),
        "iat": now, "exp": now + REFRESH_TTL,
        "typ": "refresh", "jti": refresh_id,
    }
    # Persist refresh JTI hash for revocation (store hashlib.sha256(refresh_id))
    user.refresh_token_hashes.append(hashlib.sha256(refresh_id.encode()).hexdigest())
    db.session.commit()

    private_key = current_app.config["JWT_PRIVATE_KEY"]  # PEM-encoded RSA
    return {
        "access": jwt.encode(access_payload, private_key, algorithm="RS256"),
        "refresh": jwt.encode(refresh_payload, private_key, algorithm="RS256"),
    }
```

Key choices:

- **RS256, not HS256.** Asymmetric so the mobile client can verify with a public key without holding the secret. Keys are rotated periodically; the public key is also exposed via a JWKS endpoint.
- **Short access TTL (15 min)** + **longer refresh TTL (30 days)** with refresh-token rotation: a fresh refresh token is issued on every refresh, and the old one is revoked. Stolen refresh tokens have a finite blast radius.
- **Refresh tokens are revocable** — JTI hashes stored per user. Logout clears the active JTI. Password change clears all JTIs.
- **No "remember me" concept** — the refresh token is the remember mechanism.
- The JWT layer **bypasses CSRF** because the mobile client sends the token as `Authorization: Bearer <token>` rather than as a cookie.

**Failure modes to avoid:**

- Signing with HS256 and putting the secret in a `.env` file the mobile client *also* has. (Don't.)
- Storing the refresh token in `AsyncStorage` instead of `expo-secure-store`. (Use secure-store.)
- Not revoking on logout. (Revoke.)
- Trusting an `expired` access token's claims for sensitive ops — refresh first.

---

## 12. Session + JWT coexistence

Some products serve both a Jinja-rendered web UI (sessions) and a React Native client (JWT). The same Flask app can handle both. Patterns:

- **Separate blueprints**: `app/blueprints/auth/` for the web session flow, `app/blueprints/api/auth/` for the JWT flow.
- **Different `login_required` decorators**: `flask-login`'s for sessioned routes, a `@jwt_required` decorator (custom) for API routes.
- **`User` model is shared** — same `password_hash`, same `mfa_secret`, same audit log.
- **Audit log entries name the auth path** (`web_session` vs. `api_jwt`), so abuse patterns are visible.

---

## 13. Audit log

A `LoginEvent` model (or a structured log going to whatever your log destination is):

```python
class LoginEvent(db.Model):
    id = ...
    user_id = ...  # nullable for unknown-email attempts
    event_type = db.Column(db.String(64))  # login.success, login.failed, password.reset, mfa.enrolled, ...
    ip = db.Column(db.String(64))
    user_agent = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=utcnow)
    metadata_json = db.Column(db.JSON)  # path-specific extras
```

Persist for at least 90 days. The audit log is what tells you, post-incident, what was actually done with a compromised account.

---

## 14. Rate limiting

`flask-limiter` with Redis backend:

```python
from flask_limiter import Limiter
limiter = Limiter(get_remote_address, app=app, storage_uri=app.config["REDIS_URL"])

@bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute; 30 per hour", methods=["POST"])
def login():
    ...
```

Per-IP global is the starting line. Compose with per-(IP + identifier) keys for auth-specific flows (see §6).

---

## 15. Account deletion

Two paths, both supported:

- **Soft delete + grace period.** Mark `deleted_at`; deny login; after 30 days, hard-delete user-identifying fields. Useful when "I want my account back" is a real user need.
- **Hard delete on request.** Remove personal data, anonymize logs, keep referential integrity (e.g., a record of "[deleted user]" so foreign keys don't shatter). Required by GDPR-style "right to be forgotten" requests.

Either way:

- Revoke all sessions and refresh tokens.
- Send a confirmation email at deletion-trigger time and at hard-delete time.
- Log the deletion event in a separate, retained-longer log (compliance evidence).

---

## 16. Security review checklist

Before a Flask MVP ships its auth surface:

- [ ] Argon2id password hashing in place. Bcrypt-only is a fail.
- [ ] Session backend is server-side (Redis in prod), not signed-cookie.
- [ ] Cookies: `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict` where compatible).
- [ ] Idle and absolute session expiry both enforced.
- [ ] CSRF on all state-changing routes (form + JSON header).
- [ ] No email enumeration on login, signup, or reset-request flows.
- [ ] Password reset and email verification tokens are single-use, hashed-on-storage, short-expiry.
- [ ] Email verification is enforced before login.
- [ ] Rate limiting on login, reset request, MFA challenge.
- [ ] MFA implemented (if scoped) with backup codes.
- [ ] JWT (if used): RS256, short access TTL, refresh rotation, revocable.
- [ ] Audit log writes for every auth-relevant event.
- [ ] Password-change and account-deletion flows revoke all active sessions.
- [ ] Headers: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
- [ ] Dependencies are pinned and scanned (e.g., `pip-audit` in CI).

The agent-skills `security-auditor` persona uses a checklist of similar shape. Invoke it via `/ship` or directly during code review, with a pointer to this guide.

---

## 17. Handoffs

### 17.1 Outward

- `guides/web/flask-mvp-scaffold.md` defines where auth files live (`app/blueprints/auth/`, `app/services/auth.py`, `app/extensions.py`).
- `guides/web/flask-deploy-runbook.md` §4.2 covers SSH hardening; this guide is its application-layer counterpart.
- `guides/mobile/react-native-mvp-scaffold.md` §4.5-§4.6 is the mobile-side contract; §11 here is its server-side contract.
- The `security-auditor` persona (`external/agent-skills/agents/security-auditor.md`) reviews implementations against OWASP and this guide.

### 17.2 Inward (defers to)

- OWASP ASVS (v4 or current) — comprehensive standard; this guide is a curated, MVP-scoped subset.
- The `argon2-cffi`, `flask-login`, `flask-session`, `flask-wtf`, `authlib`, and `pyjwt` documentation for API specifics.
- `guides/web/do-spaces-integration.md` §13.3 — adapt the leaked-credential drill there to also cover leaked auth tokens.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
