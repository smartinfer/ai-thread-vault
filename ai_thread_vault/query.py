from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union


def _connect(path: Union[str, Path]) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def search(path: Union[str, Path], query: str, *, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = _connect(path)
    try:
        sql = """
        SELECT
            t.id AS thread_id,
            t.title AS title,
            snippet(message_fts, 1, '[', ']', '...', 16) AS snippet
        FROM message_fts
        JOIN message AS m ON m.id = message_fts.message_id
        JOIN thread AS t ON t.id = m.thread_id
        WHERE message_fts MATCH ?
        ORDER BY bm25(message_fts), t.id
        """
        params: List[Any] = [query]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def show(path: Union[str, Path], thread_id: str) -> Dict[str, Any]:
    conn = _connect(path)
    try:
        thread = conn.execute(
            "SELECT id, title FROM thread WHERE id = ?",
            (thread_id,),
        ).fetchone()
        if thread is None:
            raise KeyError(thread_id)

        messages = conn.execute(
            "SELECT id, thread_id, role, content FROM message WHERE thread_id = ? ORDER BY id",
            (thread_id,),
        ).fetchall()
        return {
            "id": thread["id"],
            "title": thread["title"],
            "messages": [dict(row) for row in messages],
        }
    finally:
        conn.close()


def export_markdown(path: Union[str, Path], thread_id: str) -> str:
    thread = show(path, thread_id)
    lines: List[str] = [f"# {thread['title'] or thread['id']}", ""]
    for message in thread["messages"]:
        lines.append(f"## {message['role']}")
        lines.append("")
        lines.append(message["content"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def stats(path: Union[str, Path]) -> Dict[str, int]:
    conn = _connect(path)
    try:
        rows = conn.execute(
            """
            SELECT platform, COUNT(DISTINCT thread_id) AS count
            FROM thread_import
            GROUP BY platform
            ORDER BY platform
            """
        ).fetchall()
        return {row["platform"]: row["count"] for row in rows}
    finally:
        conn.close()
