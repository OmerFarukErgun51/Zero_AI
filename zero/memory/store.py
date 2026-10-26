"""Yerel kalıcı hafıza — SQLite. Kişi (profile) başına izole."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Message:
    id: int
    profile: str
    role: str
    text: str
    ts: datetime


@dataclass
class ActivitySample:
    profile: str
    app: str
    title: str
    ts: datetime


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        c = self._conn
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                ts TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS facts (
                profile TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (profile, key)
            );
            CREATE TABLE IF NOT EXISTS profiles (
                profile TEXT PRIMARY KEY,
                summary TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS embeddings (
                message_id INTEGER PRIMARY KEY,
                vector TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile TEXT NOT NULL,
                app TEXT NOT NULL,
                title TEXT NOT NULL,
                ts TEXT NOT NULL
            );
            """
        )
        c.commit()

    # --- mesajlar ---
    def add_message(self, profile: str, role: str, text: str, ts: datetime | None = None) -> int:
        ts = ts or datetime.now()
        cur = self._conn.execute(
            "INSERT INTO messages (profile, role, text, ts) VALUES (?, ?, ?, ?)",
            (profile, role, text, ts.isoformat()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def _row_to_message(self, row: sqlite3.Row) -> Message:
        return Message(
            id=row["id"],
            profile=row["profile"],
            role=row["role"],
            text=row["text"],
            ts=datetime.fromisoformat(row["ts"]),
        )

    def recent_messages(self, profile: str, limit: int = 20) -> list[Message]:
        rows = self._conn.execute(
            "SELECT * FROM messages WHERE profile = ? ORDER BY id DESC LIMIT ?",
            (profile, limit),
        ).fetchall()
        return [self._row_to_message(r) for r in reversed(rows)]

    def all_messages(self, profile: str) -> list[Message]:
        rows = self._conn.execute(
            "SELECT * FROM messages WHERE profile = ? ORDER BY id ASC",
            (profile,),
        ).fetchall()
        return [self._row_to_message(r) for r in rows]

    # --- gerçekler (facts) ---
    def set_fact(self, profile: str, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO facts (profile, key, value) VALUES (?, ?, ?) "
            "ON CONFLICT(profile, key) DO UPDATE SET value = excluded.value",
            (profile, key, value),
        )
        self._conn.commit()

    def get_facts(self, profile: str) -> dict[str, str]:
        rows = self._conn.execute(
            "SELECT key, value FROM facts WHERE profile = ?", (profile,)
        ).fetchall()
        return {r["key"]: r["value"] for r in rows}

    # --- profil özeti ---
    def set_profile_summary(self, profile: str, summary: str) -> None:
        self._conn.execute(
            "INSERT INTO profiles (profile, summary) VALUES (?, ?) "
            "ON CONFLICT(profile) DO UPDATE SET summary = excluded.summary",
            (profile, summary),
        )
        self._conn.commit()

    def get_profile_summary(self, profile: str) -> str:
        row = self._conn.execute(
            "SELECT summary FROM profiles WHERE profile = ?", (profile,)
        ).fetchone()
        return row["summary"] if row else ""

    # --- embedding'ler ---
    def set_embedding(self, message_id: int, vector: list[float]) -> None:
        self._conn.execute(
            "INSERT INTO embeddings (message_id, vector) VALUES (?, ?) "
            "ON CONFLICT(message_id) DO UPDATE SET vector = excluded.vector",
            (message_id, json.dumps(vector)),
        )
        self._conn.commit()

    def messages_with_embeddings(self, profile: str) -> list[tuple[Message, list[float]]]:
        rows = self._conn.execute(
            "SELECT m.*, e.vector AS vector FROM messages m "
            "JOIN embeddings e ON e.message_id = m.id WHERE m.profile = ? ORDER BY m.id ASC",
            (profile,),
        ).fetchall()
        out: list[tuple[Message, list[float]]] = []
        for r in rows:
            out.append((self._row_to_message(r), json.loads(r["vector"])))
        return out

    # --- etkinlik örnekleri (gün boyu takip) ---
    def add_activity_sample(self, profile: str, app: str, title: str, ts: datetime) -> None:
        self._conn.execute(
            "INSERT INTO activity (profile, app, title, ts) VALUES (?, ?, ?, ?)",
            (profile, app, title, ts.isoformat()),
        )
        self._conn.commit()

    def activity_for_day(self, profile: str, day) -> list[ActivitySample]:
        rows = self._conn.execute(
            "SELECT * FROM activity WHERE profile = ? AND substr(ts, 1, 10) = ? ORDER BY id ASC",
            (profile, day.isoformat()),
        ).fetchall()
        return [
            ActivitySample(
                profile=r["profile"],
                app=r["app"],
                title=r["title"],
                ts=datetime.fromisoformat(r["ts"]),
            )
            for r in rows
        ]
