from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any

from . import db, security
from .config import Config

DEV_USERS: dict[str, dict[str, Any]] = {
    "alice": {
        "subject": "dev:alice",
        "first_name": "Alice",
        "last_name": "Andersson",
        "person_id": "19900101-1234",
        "assurance": "eid_auth",
        "org": None,
    },
    "bob": {
        "subject": "dev:bob",
        "first_name": "Bob",
        "last_name": "Berg",
        "person_id": "19850202-5678",
        "assurance": "proxy",
        "org": None,
    },
    "agent": {
        "subject": "dev:agent",
        "first_name": "Anna",
        "last_name": "Svensson",
        "person_id": "19870303-9012",
        "assurance": "proxy",
        "org": "Nordbank",
    },
    "customer": {
        "subject": "dev:customer",
        "first_name": "Erik",
        "last_name": "Ek",
        "person_id": "19920404-3456",
        "assurance": "eid_auth",
        "org": None,
    },
}

DEV_COUNTERPARTS = {
    "dev:alice": "bob",
    "dev:bob": "alice",
    "dev:agent": "customer",
    "dev:customer": "agent",
}


@dataclass(frozen=True)
class Identity:
    subject: str
    first_name: str
    last_name: str
    person_id: str | None
    assurance: str
    org: str | None
    source: str

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class AuthContext:
    user: dict[str, Any]
    identity: Identity
    auth_session: dict[str, Any]
    csrf_token: str
    set_cookie_sid: str | None
    is_dev: bool
    source: str


def _cookie_sid(handler: Any, config: Config) -> str | None:
    raw = handler.headers.get("Cookie")
    if not raw:
        return None
    jar = SimpleCookie()
    try:
        jar.load(raw)
    except Exception:
        return None
    morsel = jar.get(config.cookie_name)
    return morsel.value if morsel else None


def cookie_header(config: Config, sid: str) -> str:
    parts = [
        f"{config.cookie_name}={sid}",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        f"Max-Age={config.auth_session_ttl_seconds}",
    ]
    if config.cookie_secure:
        parts.append("Secure")
    return "; ".join(parts)


def clear_cookie_header(config: Config) -> str:
    parts = [
        f"{config.cookie_name}=",
        "Path=/",
        "HttpOnly",
        "SameSite=Lax",
        "Max-Age=0",
    ]
    if config.cookie_secure:
        parts.append("Secure")
    return "; ".join(parts)


def _one(headers: Any, name: str, required: bool = True) -> str | None:
    values = headers.get_all(name) or []
    if not values:
        if required:
            raise ValueError(f"missing {name}")
        return None
    if len(values) != 1:
        raise ValueError(f"duplicate {name}")
    value = values[0].strip()
    if not value:
        if required:
            raise ValueError(f"empty {name}")
        return None
    return value


def _identity_from_user(config: Config, user: dict[str, Any], source: str) -> Identity:
    return Identity(
        subject=user["subject"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        person_id=security.decrypt_pn(
            config.secret_key, config.pn_encryption_key, user.get("pn_encrypted")
        ),
        assurance=user["assurance"],
        org=user.get("org"),
        source=source,
    )


def _ensure_session(
    conn: sqlite3.Connection,
    config: Config,
    user: dict[str, Any],
    existing_sid: str | None,
) -> tuple[dict[str, Any], str | None]:
    if existing_sid:
        existing = db.get_auth_session(conn, existing_sid)
        if existing and existing["subject"] == user["subject"]:
            return existing, None
        if existing:
            db.delete_auth_session(conn, existing_sid)
    created = db.create_auth_session(conn, config, user["subject"])
    return created, created["id"]


def resolve_identity(
    handler: Any, config: Config, conn: sqlite3.Connection
) -> AuthContext | None:
    sid = _cookie_sid(handler, config)
    if config.auth_mode == "dev":
        if not sid:
            return None
        auth_session = db.get_auth_session(conn, sid)
        if not auth_session:
            return None
        user = db.get_user_by_subject(conn, auth_session["subject"])
        if not user:
            return None
        identity = _identity_from_user(config, user, "dev session")
        return AuthContext(
            user=user,
            identity=identity,
            auth_session=auth_session,
            csrf_token=auth_session["csrf_token"],
            set_cookie_sid=None,
            is_dev=True,
            source="dev session",
        )

    if config.proxy_shared_secret:
        supplied = _one(handler.headers, "X-Proxy-Secret", required=False)
        if not supplied or not security.constant_time_equal(
            supplied, config.proxy_shared_secret
        ):
            return None

    try:
        subject = security.validate_subject(_one(handler.headers, "X-User-Id") or "")
        first_name = security.validate_name(_one(handler.headers, "X-Name") or "", "first name")
        last_name = security.validate_name(
            _one(handler.headers, "X-Last-Name") or "", "last name"
        )
        person_id_raw = _one(handler.headers, "X-Person-Id", required=False)
        person_id = security.normalize_pn(person_id_raw) if person_id_raw else None
        assurance_raw = _one(handler.headers, "X-Auth-Assurance", required=False) or "proxy"
        assurance = assurance_raw if assurance_raw in {"proxy", "eid_auth", "eid_sign"} else "proxy"
        org_raw = _one(handler.headers, "X-Auth-Org", required=False)
        org = security.validate_name(org_raw, "organisation") if org_raw else None
    except ValueError:
        return None

    display_name = f"{first_name} {last_name}".strip()
    user = db.get_or_create_user(
        conn,
        config,
        subject=subject,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        assurance=assurance,
        org=org,
        person_id=person_id,
    )
    auth_session, set_cookie_sid = _ensure_session(conn, config, user, sid)
    identity = _identity_from_user(config, user, "proxy headers")
    return AuthContext(
        user=user,
        identity=identity,
        auth_session=auth_session,
        csrf_token=auth_session["csrf_token"],
        set_cookie_sid=set_cookie_sid,
        is_dev=False,
        source="proxy headers",
    )


def dev_login(
    conn: sqlite3.Connection, config: Config, key: str
) -> tuple[dict[str, Any], Identity, str] | None:
    if config.auth_mode != "dev":
        return None
    data = DEV_USERS.get(key)
    if not data:
        return None
    display_name = f"{data['first_name']} {data['last_name']}".strip()
    user = db.get_or_create_user(
        conn,
        config,
        subject=data["subject"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        display_name=display_name,
        assurance=data["assurance"],
        org=data["org"],
        person_id=data["person_id"],
    )
    auth_session = db.create_auth_session(conn, config, user["subject"])
    identity = _identity_from_user(config, user, "dev session")
    return user, identity, auth_session["id"]


def logout(conn: sqlite3.Connection, config: Config, sid: str | None) -> None:
    if sid:
        db.delete_auth_session(conn, sid)


def counterpart_for(subject: str) -> str | None:
    return DEV_COUNTERPARTS.get(subject)
