import sqlite3
from typing import Iterable, Optional

from . import ImportedThread
from .clean import CleanedMessage


def store_thread(
    conn: sqlite3.Connection,
    thread: ImportedThread,
    messages: Iterable[CleanedMessage],
    *,
    platform: str,
    source_id: str,
) -> str:
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS thread_import (
            id INTEGER PRIMARY KEY,
            thread_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            source_id TEXT NOT NULL,
            UNIQUE(platform, source_id),
            FOREIGN KEY(thread_id) REFERENCES thread(id) ON DELETE CASCADE
        )
        """
    )

    existing_thread_id_row = cursor.execute(
        "SELECT thread_id FROM thread_import WHERE platform = ? AND source_id = ?",
        (platform, source_id),
    ).fetchone()
    existing_thread_id: Optional[str] = (
        existing_thread_id_row[0] if existing_thread_id_row is not None else None
    )

    target_thread_id = existing_thread_id or thread.id

    cursor.execute(
        "INSERT OR REPLACE INTO thread(id, title) VALUES(?, ?)",
        (target_thread_id, thread.title),
    )

    if existing_thread_id is not None:
        cursor.execute("DELETE FROM message_fts WHERE message_id IN (SELECT id FROM message WHERE thread_id = ?)", (existing_thread_id,))
        cursor.execute("DELETE FROM message WHERE thread_id = ?", (existing_thread_id,))

    message_count = 0
    for message in messages:
        cursor.execute(
            "INSERT OR REPLACE INTO message(id, thread_id, role, content) VALUES(?, ?, ?, ?)",
            (message.id, target_thread_id, message.role, message.content),
        )
        cursor.execute(
            "INSERT INTO message_fts(message_id, content) VALUES(?, ?)",
            (message.id, message.content),
        )
        message_count += 1

    thread_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(thread)").fetchall()
    }
    if "message_count" in thread_columns:
        cursor.execute(
            "UPDATE thread SET message_count = ? WHERE id = ?",
            (message_count, target_thread_id),
        )

    cursor.execute(
        """
        INSERT INTO thread_import(thread_id, platform, source_id)
        VALUES(?, ?, ?)
        ON CONFLICT(platform, source_id) DO UPDATE SET thread_id = excluded.thread_id
        """,
        (target_thread_id, platform, source_id),
    )

    conn.commit()
    return target_thread_id
