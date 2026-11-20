# Project Verify — Threat Model

**Status:** Draft for review  
**Version:** 0.1  
**Date:** 2026-11-18  
**Related:** [Design](design.md), [Naming](naming.md)

---

## 1. Scope

This threat model covers:

- the verification web app and its BFF,
- the boundary between the existing auth proxy and the app,
- the verification session, join token, verification code, participant roster, confirmations, and receipts,
- personal data processed by the app,
- future eID step-up (BankID/Freja).

It does **not** cover:

- the call platform (Teams, Zoom, Google Meet, telephony) or its media encryption,
- the user’s device, browser, or operating system,
- the auth proxy/IdP’s internal security beyond the trust assumptions,
- the eID provider’s internal security beyond its contractual/technical assertions,
- the customer’s network,
- legal validity of receipts.

---

## 2. Method

The analysis uses:

- **STRIDE** for a structured threat inventory,
- **attack scenarios** for the most important real-world cases,
- **trust boundaries** to show where controls must live,
- **residual risk** to state what the app cannot solve,
- **security requirements and tests** to make the mitigations verifiable.

The most important design claim to protect is:

> “Both authenticated accounts joined the same session, saw each other’s identity, and independently confirmed.”

The app must never silently upgrade that claim to:

> “The voice/video is authentic” or “The person’s legal identity is proven” unless the corresponding evidence exists.

---

## 3. Assets

| Asset | Why it matters |
|---|---|
| Identity assertions (`x-userid`, names, personal number) | Spoofing them allows impersonation |
| BFF session cookie | Hijacking it allows actions as the user |
| Join tokens | Bearer tokens; leaking one may let an unintended person join |
| Verification codes | If misused as a secret, leaking one may enable fraud; each participant receives only their own code |
| Participant roster and confirmations | Tampering can produce a false “verified” result |
| Receipts and audit logs | Evidence; tampering undermines trust and disputes |
| Personal data (names, personal numbers) | GDPR/privacy harm; identity theft |
| Availability | A verification service that is down can block legitimate calls |
| Brand/domain reputation | Phishing and social engineering rely on trust in the brand |

---

## 4. Actors

| Actor | Capability | Goal |
|---|---|---|
| **Legitimate initiator** | Authenticated account, can create sessions | Verify the other person |
| **Legitimate responder** | Authenticated account, can join | Verify the initiator |
| **External attacker** | No account; internet access; can send requests | Impersonate, join, disrupt |
| **Malicious authenticated user** | Valid account; can create/join | Spy, harass, forge a verification, escalate |
| **Compromised proxy/IdP** | Can assert any identity | Full impersonation |
| **Insider/admin** | Application access | Data theft, abuse, cover tracks |
| **Network attacker** | Can intercept/modify traffic if TLS fails | Steal sessions/data |
| **Social engineer** | Can call/email users | Trick users into revealing codes or confirming |
| **eID provider** (future) | Issues identity/signature assertions | Provide trustworthy identity; if compromised, high impact |

---

## 5. Trust boundaries

```
[User browser] --TLS--> [Auth proxy / IdP] --trusted--> [BFF / app] --private--> [Postgres]
                               |                              |
                               |                              +--mTLS--> [BankID/Freja] (future)
                               |
                        [identity assertion]
```

| Boundary | Trust level | Primary controls |
|---|---|---|
| B1: Browser ↔ proxy | Untrusted | TLS, HSTS, cookies, CSRF, CSP, authentication |
| B2: Proxy ↔ app | Trusted, but must be enforced | mTLS/private network; signed assertion; proxy strips inbound identity headers; app validates |
| B3: App ↔ database | Trusted network | Least privilege, encryption, backups, no public exposure |
| B4: App ↔ eID provider | External | mTLS, signature/cert validation, contract, monitoring |
| B5: App ↔ browser | Untrusted | Server-side authorization; no client-supplied user IDs; output escaping |

**The most important boundary is B2.** If it fails, the app’s authorization model is meaningless.

---

## 6. Assumptions

| # | Assumption | If false |
|---|---|---|
| T1 | The app is not directly reachable from the internet. | Header spoofing becomes trivial; full account takeover. |
| T2 | The proxy strips client-supplied identity headers. | An attacker can inject or duplicate identity headers. |
| T3 | The proxy-to-app connection is authenticated (mTLS or private network). | A network attacker on that segment can inject identities. |
| T4 | The proxy authenticates every request, including API, SSE, and WebSocket. | Unauthenticated access to session data. |
| T5 | TLS is correctly configured end-to-end from the browser to the proxy and from the proxy to the app. | Session/data interception. |
| T6 | The database is not publicly reachable. | Direct data theft/tampering. |
| T7 | User devices are not compromised. | Session theft, screen capture, malware. Residual risk. |
| T8 | The call platform is outside the app’s trust boundary. | The app cannot verify the call channel. |
| T9 | The proxy’s identity assurance is known and honestly labeled. | The app may overclaim legal identity. |
| T10 | The eID provider (future) is trustworthy and its signatures are verified correctly. | False identity/signature claims. |

---

## 7. STRIDE summary

| ID | Threat | Impact | Primary mitigations | Residual risk |
|---|---|---|---|---|
| **S1** | Forged identity headers | Account takeover | Network isolation; proxy strips headers; mTLS/signed assertion; fail closed | Compromised proxy |
| **S2** | Session hijack | Actions as another user | HttpOnly/Secure/SameSite cookie; CSP; short TTL; rotation; re-auth | Compromised device |
| **S3** | Fake initiator / phishing link | Victim joins attacker’s session | Verified identity display; assurance label; warnings; report; domain trust | Social engineering |
| **S4** | Code relay / voice MITM | False belief that the voice is authentic | Precise claim; video; eID sign; call-platform binding; education | Not fully solvable by a separate app |
| **S5** | Group lurker | Unverified listener in a call | Call-platform integration; roster lock; explicit UI limitation | No integration in v1 |
| **T1** | Tampered code/roster | False verification | Server-generated state; roster version; transaction; audit | Malicious server/admin |
| **T2** | Race/double confirm | Inconsistent state, duplicate receipts | Row lock; unique constraints; idempotency | None if implemented correctly |
| **T3** | Receipt tampering | False evidence | Server-side HMAC/signature; access control; verify link | Compromised server |
| **R1** | Repudiation | Dispute over whether verification happened | Audit log; receipt; optional eID signature | No legal signature in v1 |
| **I1** | Personal number leakage / on-screen exposure | Privacy harm, identity theft | Encrypt at rest; masked option; hide on tab blur; no logs/receipts; retention; access | Insider, shoulder surfing, screen capture |
| **I2** | Session data leakage | Exposure of who met whom | Authorization; IDOR tests; encryption | Insider |
| **I3** | Logs/analytics leakage | PII in third parties | Redaction; no PII analytics; self-hosted assets | Misconfiguration |
| **D1** | DoS | Verification unavailable | Rate limits; WAF; quotas; graceful degradation | Determined DDoS |
| **E1** | IDOR | Cross-user access | Resource-level authorization; opaque IDs; tests | Logic bugs |
| **E2** | Admin abuse | Data theft/modification | Least privilege; audit; break-glass; separation of duties | Malicious admin |
| **E3** | Header injection/smuggling | Identity confusion | Reject duplicates; canonical parsing; proxy strips; tests | Proxy bug |

---

## 8. Attack scenarios

### 8.1 Direct access with forged headers

**Attack:**

1. Attacker discovers the app’s IP/port or a direct ingress.
2. Sends `x-userid: victim`, `x-name: Victim`, `x-personid: ...`.
3. The app trusts the headers and creates a session as the victim.

**Impact:** full account takeover; the attacker can create/join verifications as the victim.

**Mitigations:**

- The app is not reachable except through the proxy (network policy/firewall/private subnet).
- The proxy strips inbound identity headers.
- The proxy-to-app connection uses mTLS or a signed JWT.
- The app fails closed if the assertion is missing/invalid.
- An external test tries to reach the app directly and with forged headers; it must fail.

**Residual:** if the proxy itself is compromised, the app cannot distinguish.

---

### 8.2 Header smuggling / duplicate headers

**Attack:**

1. Client sends `x-userid: attacker` and `x-userid: victim` (or a comma-joined value).
2. A misconfigured proxy appends rather than replaces.
3. The app picks the first/last value, authenticating the wrong user.

**Impact:** impersonation.

**Mitigations:**

- Proxy replaces/strips all inbound identity headers.
- App rejects duplicate headers, comma-joined values, and unexpected casing.
- App validates exactly one value per header.
- Integration tests cover duplicate/malformed headers.
- Use a signed JWT with a single canonical subject claim where possible.

**Residual:** proxy/framework parsing quirks. Test with the actual proxy.

---

### 8.3 Session hijack

**Attack:** XSS, malware, shared device, or a leaked cookie lets the attacker use the victim’s BFF session.

**Impact:** the attacker can join/confirm as the victim; the receipt may be false.

**Mitigations:**

- `__Host-` cookie; `Secure`; `HttpOnly`; `SameSite=Lax/Strict`.
- CSP; escape output; no inline scripts.
- Short idle/absolute timeout; rotate session ID on login.
- Bind the BFF session to the proxy subject; invalidate on subject change.
- Re-authenticate before eID signing (later).
- “Not you?” / logout on shared devices.
- Revoke sessions on incident.

**Residual:** a compromised device can act as the user. The app cannot fully prevent this.

---

### 8.4 Code relay / voice man-in-the-middle

**Attack:**

1. Mallory calls Alice pretending to be Bob.
2. Mallory calls Bob pretending to be Alice.
3. Alice and Bob both open the app and join the same verification session (Mallory forwards the link or persuades them to join).
4. They see each other’s real identities and each verifies the other’s code.
5. The app reports “verified” while Mallory is the voice in the middle.

**Impact:** false assurance about the call channel.

**Mitigations:**

- The app’s claim is precise: “both accounts confirmed presence”, not “the voice is authentic”.
- For high-stakes calls, require video and an eID signature at confirmation time. A deepfake/relay is harder to sustain if the person must sign a fresh challenge with BankID/Freja (though a relay of a willing signer is still possible).
- Bind the verification to the call platform’s meeting/participant identity where possible.
- UI education: “This confirms the account, not the voice. If you have not seen this person on video, treat it accordingly.”
- For customer service, use the company-initiated flow and published channels.

**Residual:** a separate web app cannot fully solve a voice/video relay. This is a fundamental limitation, not a bug.

---

### 8.5 Fake initiator / phishing link

**Attack:**

1. Attacker creates a session and sends the link to the victim, pretending to be a bank/company/friend.
2. The victim joins; the app shows the attacker’s identity (or a weak/unverified label).
3. The victim may not notice and confirms.

**Impact:** the victim believes they verified the attacker.

**Mitigations:**

- Show the initiator’s identity and assurance label prominently.
- For organizations, show the verified company brand/domain; do not allow arbitrary branding.
- Warn: “Only continue if you expected this call.”
- Allow reporting/blocking.
- For high assurance, require the initiator to be eID-verified.
- Do not use the verification code as a secret; do not ask the victim to read it to the initiator.

**Residual:** social engineering and lookalike domains.

---

### 8.6 Customer-service inbound scam

**Attack:**

1. Scammer calls a customer, claiming to be the bank/company.
2. Scammer asks the customer to “verify” by reading a code or approving a push.
3. If the app uses codes as secrets, the scammer can relay/abuse them.

**Impact:** fraud.

**Mitigations:**

- The company initiates the verification; the customer never reads a code to an inbound caller.
- The code is not used to join or authenticate; it is only compared.
- The app shows the company and agent identity; the customer confirms in the genuine app.
- Copy: “We will never call you and ask for a code.”
- Publish the official app/domain and phone number.
- Train agents and customers.

**Residual:** a customer may still be tricked into confirming a genuine session for the wrong reason. User education and eID step-up help.

---

### 8.7 Group lurker

**Attack:** an attacker listens in the call but does not join the app. The app’s group roster verifies only those who joined, so the group appears verified while the lurker listens.

**Impact:** false sense of privacy.

**Mitigations:**

- The UI says “verified participants in this app session”, not “everyone in the call”.
- The host checks the call participant list separately.
- Call-platform integration compares the call roster with the app roster and flags unverified participants (future).
- For high-stakes groups, use a platform with a verified participant list or 1:1 calls.

**Residual:** without call integration, the app cannot see the call roster.

---

### 8.8 Race condition / double confirmation

**Attack:** two tabs or concurrent requests confirm at the same time; one request confirms for both, or two receipts are created.

**Impact:** inconsistent state; false receipt; audit confusion.

**Mitigations:**

- Server identifies the participant from the BFF session, never from the body.
- `SELECT ... FOR UPDATE` on the session row.
- Unique `(session_id, user_id)` on participants.
- Unique `receipts.session_id`.
- Idempotency keys.
- Integration tests with concurrent requests.

**Residual:** implementation bugs; test thoroughly.

---

### 8.9 Code brute force

**Attack:** attacker tries codes to join/confirm.

**Impact:** unauthorized join/confirmation.

**Mitigations:**

- The verification code is **not** used to join or authenticate.
- Join uses a 256-bit single-use token.
- If a short room code is offered for convenience, it is rate-limited, short-lived, and bound to the session; it is not the only factor.
- Rate limits per session/user/IP; lockout after repeated failures.
- Audit failed attempts.

**Residual:** a leaked join token can be used once; the initiator sees the joiner’s identity and can cancel.

---

### 8.10 Replay of join link

**Attack:** a join link is forwarded or leaked; an attacker opens it first and joins as the responder.

**Impact:** wrong person in the session.

**Mitigations:**

- Join token is single-use and short-lived; stored hashed.
- The initiator sees the joiner’s identity and can cancel before confirming.
- For higher assurance, bind the invite to an expected identity (email/phone/PN hash) or require eID.
- Do not put the token in referrer headers; use `Referrer-Policy: no-referrer`.
- Consume the token on first successful join.

**Residual:** a leaked token can still be used by the first authenticated joiner. Participant approval is the backstop.

---

### 8.11 Personal number leakage and in-session display

**Attack/accident:** full personal numbers end up in proxy logs, APM traces, error reports, browser dev tools, analytics, receipts, or database backups. Separately, the product requirement allows full display in the session, which creates a shoulder-surfing and screen-capture risk.

**Impact:** privacy harm, identity theft, fraud, GDPR breach.

**Mitigations:**

- Encrypt the personal number at rest with Fernet; use a key from a secret manager.
- Never log headers, bodies, tokens, codes, cookies, or personal numbers.
- Redact error reporting and analytics.
- Receipts always use the masked form.
- Default to masked display where the workflow allows; full display is an explicit session choice.
- Hide the full number when the tab loses visibility; require a click to show it again.
- Warn the user that the screen is sensitive; do not show it during screen sharing if avoidable.
- Restrict access, retention, and exports; DPIA and privacy notice.
- Test log output for PII patterns.

**Residual:** shoulder surfing, screen recording, a compromised device, insider access, misconfiguration.

---

### 8.12 Receipt forgery

**Attack:** attacker edits a PDF/JSON receipt to claim a verification that did not happen.

**Impact:** false evidence.

**Mitigations:**

- Server-side receipt with an HMAC/signature.
- Optional eID signature over a canonical payload.
- A “verify receipt” endpoint that checks the integrity and returns the server’s record.
- Access control: only participants (and authorized support) can view.
- Do not rely on an unguessable URL alone.
- If used as legal evidence, use a QTSP/qualified timestamp.

**Residual:** a compromised server can forge receipts. eID signatures reduce this for the signer’s statement.

---

### 8.13 Compromised proxy / IdP

**Attack:** an attacker who controls the proxy can assert any identity.

**Impact:** full impersonation; the app cannot compensate.

**Mitigations:**

- Treat the proxy as a high-value system: hardening, patching, least privilege, separate admin plane, monitoring.
- Signed assertions with short expiry; validate issuer/audience.
- Network segmentation; mTLS; no direct app access.
- Anomaly detection on identity header patterns.
- eID step-up for high-assurance actions, so the proxy alone is not enough.
- Incident response and kill switch.

**Residual:** a fully compromised proxy can still impersonate users for lower-assurance actions.

---

### 8.14 Shared device / SSO session switching

**Attack/accident:** a kiosk or shared browser retains the previous user’s proxy session; the next person acts as the previous user.

**Impact:** wrong identity; false verification.

**Mitigations:**

- Bind the BFF session to the subject; detect changes.
- Short sessions; explicit logout; “Not you?” control.
- Kiosk mode with separate profiles or re-authentication.
- Do not allow one-device handover in the in-person flow without re-auth.

**Residual:** user error.

---

### 8.15 Deepfake / synthetic voice

**Attack:** attacker uses a deepfake voice/video while using their own or a compromised account.

**Impact:** the visual/voice evidence is misleading; the app’s identity claim may still be technically correct.

**Mitigations:**

- Do not claim the app verifies the voice.
- Require eID signing at the moment for high-stakes calls.
- Use a challenge that requires live interaction with the app (e.g., sign a fresh nonce), not just a pre-recorded phrase.
- Encourage video and out-of-band confirmation.
- Educate users.

**Residual:** deepfakes are an evolving threat; no single control is sufficient.

---

## 9. Residual risks

These are accepted or explicitly out of scope for v1:

1. **Voice/video relay and deepfakes.** A separate web app cannot verify the call channel.
2. **Compromised user device.** Malware can act as the user.
3. **Compromised proxy/IdP.** The app trusts the proxy’s identity assertions.
4. **Social engineering/coercion.** A user can be tricked or forced to confirm.
5. **Weak identity assurance.** Corporate SSO is not a legal identity.
6. **Group lurkers.** Without call-platform integration, the app cannot see the call roster.
7. **BankID/Freja coverage.** Not available to all users; international coverage needs other providers.
8. **Legal validity.** v1 receipts are audit records, not qualified signatures.
9. **User fatigue.** Users may blindly click confirm; UX and testing must address this.
10. **On-screen personal number exposure.** Full display is a product requirement; shoulder surfing, screen sharing, and screen recording remain residual risks. The masked mode is the safer default for lower-risk workflows.

---

## 10. Security requirements and tests

### 10.1 Requirements

| ID | Requirement |
|---|---|
| SR1 | The app MUST NOT be reachable except through the auth proxy. |
| SR2 | The proxy MUST strip all client-supplied identity headers. |
| SR3 | The proxy-to-app connection MUST be authenticated (mTLS) or use a signed assertion. |
| SR4 | The app MUST fail closed on missing, duplicate, malformed, or expired identity assertions. |
| SR5 | The app MUST create its own BFF session and MUST NOT accept a user ID from the client. |
| SR6 | The BFF cookie MUST be `__Host-`, `Secure`, `HttpOnly`, and `SameSite=Lax` or `Strict`. |
| SR7 | State-changing requests MUST be CSRF-protected. |
| SR8 | The app MUST enforce resource-level authorization on every session/receipt/event. |
| SR9 | The join token MUST be 256-bit random, single-use, hashed at rest, and short-lived. |
| SR10 | Each participant’s verification code MUST be unique, CSPRNG-generated, short-lived, and MUST NOT be used for join/auth. The API MUST NOT expose the other participant’s code. |
| SR11 | The server MUST require all required participants to confirm; one confirmation MUST NOT verify. |
| SR12 | Confirmations MUST be bound to the roster version; roster changes MUST invalidate them. |
| SR13 | Confirmation MUST be transactional and idempotent; exactly one receipt per verified session. |
| SR14 | Receipts MUST be access-controlled and integrity-protected. |
| SR15 | Full personal numbers MUST be encrypted at rest, MUST NOT be logged, and MUST NOT be stored in receipts. In-session display is allowed only by the session’s `pn_mode` or an explicit participant reveal. |
| SR16 | Logs MUST redact tokens, codes, cookies, and personal numbers. |
| SR17 | Rate limits MUST apply to create/join/confirm and MUST be shared across instances. |
| SR18 | SSE/WebSocket endpoints MUST require authorization and Origin validation. |
| SR19 | Sessions MUST expire server-side; expired sessions MUST NOT be confirmed. |
| SR20 | Anomalies (failed joins, repeated mismatches, header anomalies) MUST be auditable and alertable. |

### 10.2 Test plan

| Test | Expected result |
|---|---|
| Direct request to app bypassing proxy | Connection refused / 403 |
| Forged `x-userid` from outside | Rejected; no session |
| Duplicate `x-userid` headers | Rejected |
| Oversized/CRLF header values | Rejected |
| Missing identity header | 401/403; fail closed |
| Subject changes mid-session | Session invalidated |
| IDOR: Alice reads Bob’s session | 403/404 |
| IDOR: Alice downloads Bob’s receipt | 403/404 |
| CSRF: cross-site POST | Rejected |
| XSS: `<script>` in name/context | Escaped; no execution |
| Race: two simultaneous confirmations | One verified state; one receipt |
| Replay: used join token | Rejected |
| Expiry: confirm after TTL | Rejected |
| Rate limit: many create/join attempts | 429; no state change |
| SSE without session | Rejected |
| Receipt tamper | Integrity check fails |
| Log inspection | No PN/code/token/cookie |
| Group roster change after confirm | Confirmations invalidated; re-confirm required |
| One-sided confirmation | Not verified; no receipt |
| Mismatch | `mismatch`; no receipt |

### 10.3 Before production

- Threat-model review with engineering and product.
- Penetration test of the app and proxy boundary.
- Load test for concurrent sessions/SSE.
- Privacy review/DPIA.
- Incident response tabletop.
- Backup/restore test.
- Dependency/container scan.
- Accessibility audit.

---

## 11. Incident response

### 11.1 Detection

- Alert on spikes in failed joins, mismatches, created sessions, 4xx/5xx, and identity header anomalies.
- Monitor for direct-access attempts and unusual proxy-to-app traffic.
- Monitor eID failures/outages (future).

### 11.2 Response

1. **Contain:** enable the kill switch for new verifications; keep existing sessions readable if safe.
2. **Revoke:** invalidate BFF sessions, join tokens, and active verification sessions as needed.
3. **Rotate:** session keys, HMAC pepper, proxy credentials, eID certificates.
4. **Preserve:** audit logs, events, receipts; follow chain-of-custody.
5. **Notify:** follow GDPR breach notification (72 hours where required), contractual, and internal processes.
6. **Recover:** restore service; verify integrity; communicate.
7. **Postmortem:** root cause, timeline, impact, corrective actions.

### 11.3 Kill switch

- A configuration flag that disables session creation and confirmation while leaving receipts/audit accessible.
- Tested regularly.
- Requires privileged access and audit.

---

## 12. Review checklist

Use this before approving the design or a release:

- [ ] The app is not directly reachable.
- [ ] The proxy strips inbound identity headers; tested.
- [ ] Identity assertions are signed/mTLS; validated.
- [ ] The app fails closed on bad identity.
- [ ] No user ID from the client is trusted.
- [ ] BFF cookies are secure.
- [ ] CSRF, XSS, CSP, clickjacking controls are in place.
- [ ] Join token is single-use/hashed/TTL.
- [ ] Verification code is not used for join/auth.
- [ ] Both participants must verify the other person’s code.
- [ ] Roster versioning invalidates stale confirmations.
- [ ] Confirmation is transactional/idempotent.
- [ ] Receipts are integrity-protected and access-controlled.
- [ ] No full PN in browser/logs/receipts.
- [ ] Rate limits are shared across instances.
- [ ] SSE is authorized.
- [ ] Audit events are append-only and redacted.
- [ ] Tests cover forged headers, IDOR, CSRF, XSS, race, replay, expiry.
- [ ] Privacy notice/DPIA are in place.
- [ ] Incident response and kill switch are tested.
- [ ] The UI does not overclaim what was verified.
