# Samsyn

**Status:** v0.1 implementation — working app, container, and GHCR pipeline.  
**Working name:** Samsyn. It is **not trademark-cleared**; see [docs/naming.md](docs/naming.md).  
**Design:** dark, clear interface inspired by [apps.bergling.net](https://apps.bergling.net), simplified for end users.

Samsyn is a web app for **mutual verification between people in a call**. Two authenticated people join a short session, see each other’s identity and assurance level, compare a per-session code, and independently confirm. The result is an integrity-protected receipt.

It sits behind an existing secure proxy. The app has no password login of its own, but it still enforces authorization, session security, CSRF, rate limits, audit, and privacy.

---

## What is in the app

- Server-rendered pages with a dark/light theme, a simple two-action home screen, and responsive layout.
- Real server-side sessions, SQLite persistence, CSRF protection, rate limits, and audit events.
- Proxy-header authentication (`X-User-Id`, `X-Name`, `X-Last-Name`, `X-Person-Id`).
- A development mode with mock identities for local testing.
- 1:1 call, customer-service, and in-person flows.
- Per-session 6-digit + 3-word verification code; single-use 256-bit join token.
- Both participants must confirm; one-sided confirmation never verifies.
- Full personal number display as a controlled “sensitive” view, encrypted at rest, never logged, never written to receipts.
- Receipts with HMAC-SHA256 integrity, JSON download, and print/PDF.
- A plain-language Safety page explaining what is and is not verified.
- Dockerfile, Compose files, CI, and a GitHub Actions workflow that publishes to GHCR.

Group verification is deliberately not in v0.1. The data model and design leave room for it, but group roster verification needs its own phase.

---

## Quick start (local, no Node required)

Requirements: Python 3.11+ (3.14 recommended). No Node.js, npm, or frontend build step.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

export AUTH_MODE=dev
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
export COOKIE_SECURE=0
export BASE_URL=http://127.0.0.1:8080
python3 -m app
```

Open <http://127.0.0.1:8080>. Choose a mock identity on the sign-in page. To simulate two people, use two tabs/windows and the **Open as Bob/Customer** button on the invite screen; the development link logs the second tab in as the counterpart.

Or use the included Compose file:

```bash
docker compose up --build
```

The app uses SQLite at `DATA_DIR/samsyn.db` (default `./data/samsyn.db`).

---

## Development mode vs production proxy mode

### `AUTH_MODE=dev`

- Adds a mock sign-in page with Alice, Bob, Anna (Nordbank agent), and Erik (customer).
- `/dev/login` exists only in dev mode.
- **Never expose dev mode to the internet.** Anyone who can reach it can choose an identity.

### `AUTH_MODE=proxy` (default)

The app expects the reverse proxy / IdP to authenticate the user and inject:

| Header | Required | Notes |
|---|---|---|
| `X-User-Id` | Yes | Stable, opaque subject. Do not use the personal number. |
| `X-Name` | Yes | Given name. |
| `X-Last-Name` | Yes | Surname. |
| `X-Person-Id` | No | Swedish personal number or comparable ID. Sensitive; stored encrypted. |
| `X-Auth-Assurance` | No | `proxy`, `eid_auth`, or `eid_sign`. Defaults to `proxy`. |
| `X-Auth-Org` | No | Organisation/company label for customer-service flows. |
| `X-Proxy-Secret` | Optional | Shared secret between proxy and app when `PROXY_SHARED_SECRET` is set. |

**The proxy must:**

1. Authenticate every request.
2. **Strip any client-supplied copies** of these headers.
3. Inject them only after authentication.
4. Protect the proxy-to-app leg with mTLS or the shared secret.
5. Prevent direct access to the app port.
6. Set `X-Auth-Assurance` honestly if the identity is eID-verified.

If the app is directly reachable, anyone can forge `X-User-Id`. The app cannot distinguish a forged header from a proxy-injected one. Network isolation and proxy header stripping are mandatory.

Production environment example:

```bash
AUTH_MODE=proxy
SECRET_KEY=<long random secret>
PN_ENCRYPTION_KEY=<optional separate 32+ char key>
PROXY_SHARED_SECRET=<optional proxy shared secret>
COOKIE_SECURE=1
BASE_URL=https://verify.example.se
PROXY_LOGOUT_URL=https://sso.example.se/logout
DATA_DIR=/data
```

---

## Full personal number: the decision and the controls

The product decision is that the full personal number **must be displayable** during verification. The implementation treats that as a high-risk feature:

- The session creator chooses **Full** or **Masked** detail.
- Full mode displays the number in the session identity cards.
- Masked mode shows `1990••••-••••`; a participant can explicitly share their own full number.
- The number is encrypted at rest with Fernet; the key is derived from `SECRET_KEY` or a separate `PN_ENCRYPTION_KEY`.
- It is **never** written to receipts, logs, analytics, URLs, or QR codes.
- The UI hides the number when the tab loses visibility; the user can show it again.
- Receipts always use the masked form.
- A privacy/DPIA review is still required before production.

If you do not need full display, set the default to masked in `app/templates/home.html` and remove the full option; the backend supports both.

---

## Docker

```bash
docker build -t samsyn:dev .

docker run --rm -p 8080:8080 \
  -e AUTH_MODE=dev \
  -e SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')" \
  -e COOKIE_SECURE=0 \
  -e DATA_DIR=/data \
  -v samsyn-data:/data \
  samsyn:dev
```

The image runs as a non-root user, exposes port `8080`, and has a `/healthz` health check.

For production:

```bash
cp .env.example .env
# edit .env, then:
docker compose -f compose.prod.yaml up -d
```

The production compose file expects the image `ghcr.io/rogerbergling/samsyn:latest`. Change the image if the repository name differs.

---

## GHCR (GitHub Container Registry)

The workflow `.github/workflows/container.yml` builds on pushes to `main`, version tags `v*`, and manual dispatch. It publishes multi-arch images (`linux/amd64`, `linux/arm64`) with SBOM and provenance:

```
ghcr.io/rogerbergling/samsyn:latest
ghcr.io/rogerbergling/samsyn:sha-<commit>
ghcr.io/rogerbergling/samsyn:v0.1.0
```

The workflow uses the repository `GITHUB_TOKEN` with `packages: write`. If the package is private, authenticate before pulling:

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <github-user> --password-stdin
docker pull ghcr.io/rogerbergling/samsyn:latest
```

Package visibility is controlled in the GitHub package settings. A private repository does **not** automatically make the package public; GitHub packages are private by default.

---

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The suite covers:

- health and dev login,
- CSRF enforcement,
- forged `X-User-Id` ignored in dev,
- full create/join/confirm/receipt flow,
- single-use join tokens and IDOR,
- mismatch with no receipt,
- masked-number reveal,
- server-side expiry,
- personal-number encryption at rest,
- proxy-mode header authentication and shared-secret rejection.

---

## Project layout

```
app/
  __main__.py        entry point and cleanup worker
  config.py          environment configuration
  db.py              SQLite schema and persistence helpers
  auth.py            proxy/dev identity resolution, sessions, CSRF
  verification.py    session state machine, codes, confirmations, receipts
  security.py        tokens, encryption, masking, HMAC, validation
  web.py             HTTP server, routes, security headers, rate limits
  templates/         Jinja2 pages
  static/            design-system CSS, theme, app JS, favicon
tests/
  test_app.py        end-to-end HTTP tests
docs/
  design.md          product/architecture design
  threat-model.md    STRIDE analysis and residual risks
  naming.md          preliminary name check
  deployment.md      proxy and container deployment notes
Dockerfile
compose.yaml         local dev
compose.prod.yaml    production image
.github/workflows/   CI + GHCR
```

---

## Security boundaries and limitations

Samsyn proves **account presence in the same session**, not the call channel:

- It does **not** prove that the voice or video stream is authentic.
- It does **not** prove that a device or account is not compromised.
- It does **not** detect a group-call listener who never joins the app.
- A corporate SSO name is not a legal identity; the assurance label stays honest.
- BankID/Freja are **not** integrated in v0.1. If the proxy provides eID assurance, set `X-Auth-Assurance`; otherwise the app labels the identity as proxy-authenticated.
- Receipts are audit records, not qualified electronic signatures.

Read [docs/security-model notes](docs/threat-model.md) and the in-app `/security` page.

---

## Naming

The working name is **Samsyn**, chosen by the product owner for the prototype despite a preliminary conflict check. There is prior use in the same space (IKEA Samsyn video customer service, Sambruk’s Samsyn, Samsyn AB, samsyn.io) and the `.se`/`.com`/`.app` domains are registered. Do not invest in branding or domains until a proper trademark/domain clearance is done. See [docs/naming.md](docs/naming.md).

---

## Documentation

- [Design](docs/design.md)
- [Threat model](docs/threat-model.md)
- [Naming](docs/naming.md)
- [Deployment](docs/deployment.md)
