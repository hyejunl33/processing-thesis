"""SQLite event store for student manipulation logs."""

from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from pathlib import Path

from .models import Event

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("DATABASE_PATH", str(ROOT / "data" / "events.db")))


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                problem_id TEXT,
                ts REAL NOT NULL,
                type TEXT NOT NULL,
                target TEXT,
                payload TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id, ts)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_problem ON events(problem_id, ts)")


def save_event(event: Event) -> int:
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO events (session_id, problem_id, ts, type, target, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event.session_id,
                event.problem_id,
                event.ts,
                event.type,
                event.target,
                json.dumps(event.payload, ensure_ascii=False),
            ),
        )
        return int(cur.lastrowid)


def session_report(session_id: str) -> dict:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY ts ASC", (session_id,)
        ).fetchall()

    events = [
        {
            "id": row["id"],
            "session_id": row["session_id"],
            "problem_id": row["problem_id"],
            "ts": row["ts"],
            "type": row["type"],
            "target": row["target"],
            "payload": json.loads(row["payload"]),
        }
        for row in rows
    ]
    counts = Counter(e["type"] for e in events)
    return {
        "session_id": session_id,
        "count": len(events),
        "types": dict(counts),
        "first_ts": events[0]["ts"] if events else None,
        "last_ts": events[-1]["ts"] if events else None,
        "events": events,
    }
