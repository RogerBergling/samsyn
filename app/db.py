from __future__ import annotations

import json
import sqlite3
from datetime import timedelta
from typing import Any

from . import security
from .config import Config

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    assurance TEXT NOT NULL DEFAULT 'proxy',
    org TEXT,
    pn_encrypted TEXT,
    pn_masked TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires ON auth_sessions(expires_at);

CREATE TABLE IF NOT EXISTS verifications (
    id TEXT PRIMARY KEY,
    public_ref TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    state TEXT NOT NULL,
    initiator_id TEXT NOT NULL REFERENCES users(id),
    context TEXT NOT NULL DEFAULT '',
    pn_mode TEXT NOT NULL DEFAULT 'full',
    join_token_hash TEXT NOT NULL,
    join_token_enc TEXT NOT NULL,
    join_token_used_at TEXT,
    code TEXT NOT NULL,
    words TEXT NOT NULL,
    roster_version INTEGER NOT NULL DEFAULT 1,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    version INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_verifications_state_expires
    ON verifications(state, expires_at);
CREATE INDEX IF NOT EXISTS idx_verifications_join_token
    ON verifications(join_token_hash);

CREATE TABLE IF NOT EXISTS participants (
    id TEXT PRIMARY KEY,
    verification_id TEXT NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id),
    role TEXT NOT NULL,
    subject TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    assurance TEXT NOT NULL,
    org TEXT,
    pn_encrypted TEXT,
    pn_masked TEXT,
    joined_at TEXT NOT NULL,
    confirmed_at TEXT,
    decision TEXT,
    confirmed_roster_version INTEGER,
    revealed_at TEXT,
    UNIQUE(verification_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_participants_session ON participants(verification_id);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verification_id TEXT NOT NULL REFERENCES verifications(id) ON DELETE CASCADE,
    actor_id TEXT,
    type TEXT NOT NULL,
    data TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    ip_hash TEXT,
    ua_hash TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(verification_id, id);

CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    verification_id TEXT NOT NULL UNIQUE REFERENCES verifications(id) ON DELETE CASCADE,
    payload TEXT NOT NULL,
    integrity_hmac TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def connect(config: Config) -> sqlite3.Connection:
    conn = sqlite3.connect(config.database_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db(config: Config) -> None:
    conn = connect(config)
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def get_or_create_user(
    conn: sqlite3.Connection,
    config: Config,
    *,
    subject: str,
    first_name: str,
    last_name: str,
    display_name: str,
    assurance: str,
    org: str | None,
    person_id: str | None,
) -> dict[str, Any]:
    now = security.iso()
    pn_encrypted = security.encrypt_pn(config.secret_key, config.pn_encryption_key, person_id)
    pn_masked = security.mask_pn(person_id) if person_id else None
    existing = conn.execute("SELECT * FROM users WHERE subject = ?", (subject,)).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE users
               SET first_name = ?, last_name = ?, display_name = ?,
                   assurance = ?, org = ?, updated_at = ?,
                   pn_encrypted = COALESCE(?, pn_encrypted),
                   pn_masked = COALESCE(?, pn_masked)
             WHERE id = ?
            """,
            (
                first_name,
                last_name,
                display_name,
                assurance,
                org,
                now,
                pn_encrypted,
                pn_masked,
                existing["id"],
            ),
        )
        conn.commit()
        return dict(conn.execute("SELECT * FROM users WHERE id = ?", (existing["id"],)).fetchone())

    user_id = security.new_id()
    conn.execute(
        """
        INSERT INTO users
            (id, subject, first_name, last_name, display_name, assurance, org,
             pn_encrypted, pn_masked, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            subject,
            first_name,
            last_name,
            display_name,
            assurance,
            org,
            pn_encrypted,
            pn_masked,
            now,
            now,
        ),
    )
    conn.commit()
    return dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


def get_user(conn: sqlite3.Connection, user_id: str) -> dict[str, Any] | None:
    return row_to_dict(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())


def get_user_by_subject(conn: sqlite3.Connection, subject: str) -> dict[str, Any] | None:
    return row_to_dict(conn.execute("SELECT * FROM users WHERE subject = ?", (subject,)).fetchone())


def create_auth_session(conn: sqlite3.Connection, config: Config, subject: str) -> dict[str, Any]:
    session_id = security.new_token()
    csrf = security.new_csrf_token()
    now = security.utcnow()
    expires = now + timedelta(seconds=config.auth_session_ttl_seconds)
    conn.execute(
        """
        INSERT INTO auth_sessions
            (id, subject, csrf_token, created_at, expires_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, subject, csrf, security.iso(now), security.iso(expires), security.iso(now)),
    )
    conn.commit()
    return {
        "id": session_id,
        "subject": subject,
        "csrf_token": csrf,
        "created_at": security.iso(now),
        "expires_at": security.iso(expires),
        "last_seen_at": security.iso(now),
    }


def get_auth_session(conn: sqlite3.Connection, session_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM auth_sessions WHERE id = ?", (session_id,)).fetchone()
    if not row:
        return None
    if security.parse_iso(row["expires_at"]) <= security.utcnow():
        conn.execute("DELETE FROM auth_sessions WHERE id = ?", (session_id,))
        conn.commit()
        return None
    conn.execute(
        "UPDATE auth_sessions SET last_seen_at = ? WHERE id = ?",
        (security.iso(), session_id),
    )
    conn.commit()
    return dict(row)


def delete_auth_session(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("DELETE FROM auth_sessions WHERE id = ?", (session_id,))
    conn.commit()


def cleanup(conn: sqlite3.Connection, config: Config) -> None:
    now = security.iso()
    conn.execute(
        """
        UPDATE verifications
           SET state = 'expired', version = version + 1
         WHERE state IN ('waiting', 'ready', 'confirming')
           AND expires_at <= ?
        """,
        (now,),
    )
    conn.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (now,))
    conn.commit()


def audit(
    conn: sqlite3.Connection,
    *,
    verification_id: str,
    actor_id: str | None,
    event_type: str,
    data: dict[str, Any] | None = None,
    ip_hash: str | None = None,
    ua_hash: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO events (verification_id, actor_id, type, data, created_at, ip_hash, ua_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            verification_id,
            actor_id,
            event_type,
            json.dumps(data or {}, ensure_ascii=False, separators=(",", ":")),
            security.iso(),
            ip_hash,
            ua_hash,
        ),
    )
