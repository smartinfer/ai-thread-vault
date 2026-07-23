import json
from pathlib import Path

from ai_thread_vault import ImportedThread


def parse(src: str) -> list[ImportedThread]:
    path = Path(src)
    with path.open("r", encoding="utf-8") as fh:
        records = json.load(fh)

    threads: list[ImportedThread] = []
    for record in records:
        thread_id = record.get("id")
        if not thread_id:
            continue
        threads.append(
            ImportedThread(
                id=str(thread_id),
                title=record.get("name") or record.get("title"),
            )
        )
    return threads
