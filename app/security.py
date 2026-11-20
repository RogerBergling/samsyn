from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Iterable

from cryptography.fernet import Fernet, InvalidToken

WORDS: tuple[str, ...] = (
    "katt",
    "berg",
    "cykel",
    "sol",
    "hav",
    "sten",
    "lampa",
    "tåg",
    "fågel",
    "bro",
    "eld",
    "snö",
    "fönster",
    "nyckel",
    "båt",
    "skog",
    "moln",
    "stjärna",
    "väg",
    "port",
    "bord",
    "stol",
    "frukt",
    "blomma",
    "vind",
    "regn",
    "sand",
    "klippa",
    "spegel",
    "bok",
    "penna",
    "musik",
    "träd",
    "gräs",
    "fjäll",
    "dal",
    "sjö",
    "ö",
    "hage",
    "lugn",
)

_TERMINAL_STATES = {"verified", "mismatch", "expired", "cancelled"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    value = dt or utcnow()
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def new_id() -> str:
    return secrets.token_hex(16)


def new_token() -> str:
    return secrets.token_urlsafe(32)


def new_public_ref() -> str:
    alphabet = string.ascii_uppercase + string.digits
    body = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"VS-{body}"


def new_code() -> str:
    digits = "".join(secrets.choice(string.digits) for _ in range(6))
    return f"{digits[:3]} {digits[3:]}"


def new_words() -> list[str]:
    return secrets.SystemRandom().sample(WORDS, 3)


def normalize_code(value: str | None) -> str:
    """Return the six-digit part of a spoken/read code."""
    digits = re.sub(r"\D", "", value or "")
    return digits[:6]


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _fernet_key(secret_key: str, pn_key: str | None) -> bytes:
    material = (pn_key or secret_key).encode("utf-8")
    return base64.urlsafe_b64encode(hashlib.sha256(material + b"|samsyn-pn-v1").digest())


def encrypt_value(secret_key: str, pn_key: str | None, value: str | None) -> str | None:
    if not value:
        return None
    return Fernet(_fernet_key(secret_key, pn_key)).encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_value(secret_key: str, pn_key: str | None, token: str | None) -> str | None:
    if not token:
        return None
    try:
        return Fernet(_fernet_key(secret_key, pn_key)).decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None


def encrypt_pn(secret_key: str, pn_key: str | None, value: str | None) -> str | None:
    return encrypt_value(secret_key, pn_key, value)


def decrypt_pn(secret_key: str, pn_key: str | None, token: str | None) -> str | None:
    return decrypt_value(secret_key, pn_key, token)


def normalize_pn(value: str) -> str:
    cleaned = re.sub(r"[^0-9-]", "", value.strip())
    return cleaned[:20]


def mask_pn(value: str | None) -> str:
    if not value:
        return "—"
    digits = re.sub(r"\D", "", value)
    if len(digits) < 4:
        return "••••"
    return f"{digits[:4]}••••-••••"


def validate_subject(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 128:
        raise ValueError("invalid subject")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("invalid subject")
    return value


def validate_name(value: str, field: str) -> str:
    value = " ".join(value.strip().split())
    if not value or len(value) > 100:
        raise ValueError(f"invalid {field}")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError(f"invalid {field}")
    return value


def validate_context(value: str | None) -> str:
    if not value:
        return ""
    value = " ".join(value.strip().split())
    if len(value) > 200:
        raise ValueError("context is too long")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("context contains control characters")
    return value


def validate_kind(value: str) -> str:
    allowed = {"one_to_one", "customer_service", "in_person"}
    if value not in allowed:
        raise ValueError("unsupported verification type")
    return value


def validate_pn_mode(value: str) -> str:
    if value not in {"full", "masked"}:
        raise ValueError("invalid personal-number mode")
    return value


def initials(display_name: str) -> str:
    parts = [part for part in display_name.split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def assurance_label(assurance: str, mock: bool = False) -> str:
    labels = {
        "proxy": "Signed in via proxy",
        "eid_auth": "eID verified",
        "eid_sign": "eID signed",
    }
    label = labels.get(assurance, "Account signed in")
    return f"{label} (mock)" if mock else label


def kind_label(kind: str) -> str:
    return {
        "one_to_one": "1:1 call",
        "customer_service": "Customer service",
        "in_person": "In person",
    }.get(kind, kind)


def state_label(state: str) -> str:
    return {
        "waiting": "Waiting",
        "ready": "Ready",
        "confirming": "Confirming",
        "verified": "Verified",
        "mismatch": "Mismatch",
        "expired": "Expired",
        "cancelled": "Cancelled",
    }.get(state, state)


def role_label(role: str) -> str:
    return {
        "initiator": "Initiator",
        "responder": "Responder",
        "host": "Host",
        "member": "Participant",
    }.get(role, role)


def is_terminal(state: str) -> bool:
    return state in _TERMINAL_STATES


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def safe_next(value: str | None) -> str:
    if not value or not value.startswith("/") or value.startswith("//"):
        return "/"
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        return "/"
    return value


def extract_join_token(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    marker = "/join/"
    if marker in value:
        value = value.split(marker, 1)[1]
    value = value.split("?", 1)[0].split("#", 1)[0].strip("/")
    return re.sub(r"[^A-Za-z0-9_-]", "", value)


def canonical_json(payload: Any) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def receipt_hmac(secret_key: str, payload: Any) -> str:
    return hmac.new(secret_key.encode("utf-8"), canonical_json(payload), hashlib.sha256).hexdigest()


def hash_ip(secret_key: str, value: str | None) -> str | None:
    if not value:
        return None
    return hmac.new(secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()[:32]


def hash_ua(secret_key: str, value: str | None) -> str | None:
    if not value:
        return None
    return hmac.new(
        secret_key.encode("utf-8"), value.encode("utf-8", "replace"), hashlib.sha256
    ).hexdigest()[:32]


def constant_time_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left.encode("utf-8"), right.encode("utf-8"))


def join_url(base_url: str, token: str) -> str:
    return f"{base_url.rstrip('/')}/join/{token}"
