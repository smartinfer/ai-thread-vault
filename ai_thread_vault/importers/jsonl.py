import json
from pathlib import Path

from ai_thread_vault import ImportedThread, ImportedMessage


def parse(src: str) -> list[ImportedThread]:
    threads: dict[str, ImportedThread] = {}
    order: list[str] = []
    with Path(src).open("r", encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            tid = str(r.get("thread_id") or r.get("id") or "")
            if not tid:
                continue
            if tid not in threads:
                threads[tid] = ImportedThread(id=tid, title=r.get("title"))
                order.append(tid)
            threads[tid].messages.append(ImportedMessage(
                id=str(r.get("id") or f"{tid}-{i}"), thread_id=tid,
                role=r.get("role", "user"), content=r.get("content", "")))
    return [threads[t] for t in order]
