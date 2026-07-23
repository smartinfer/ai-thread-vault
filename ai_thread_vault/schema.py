import sqlite3
from pathlib import Path
from typing import Union


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS thread (
    id TEXT PRIMARY KEY,
    title TEXT
);

CREATE TABLE IF NOT EXISTS message (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(thread_id) REFERENCES thread(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS artifact (
    id INTEGER PRIMARY KEY,
    message_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(message_id) REFERENCES message(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tag (
    id INTEGER PRIMARY KEY,
    thread_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY(thread_id) REFERENCES thread(id) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5(
    message_id UNINDEXED,
    content
);
"""


def init_db(path: Union[str, Path]) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn
