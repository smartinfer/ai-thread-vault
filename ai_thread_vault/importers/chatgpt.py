import json
from pathlib import Path
from zipfile import ZipFile

from ai_thread_vault import ImportedThread


def _iter_conversations(src: str):
    path = Path(src)
    if path.is_dir():
        conversations_path = path / "conversations.json"
        with conversations_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    with ZipFile(path) as zf:
        with zf.open("conversations.json") as fh:
            return json.load(fh)


def parse(src: str) -> list[ImportedThread]:
    conversations = _iter_conversations(src)
    threads: list[ImportedThread] = []
    for conversation in conversations:
        thread_id = conversation.get("id")
        if not thread_id:
            continue
        threads.append(
            ImportedThread(
                id=str(thread_id),
                title=conversation.get("title"),
            )
        )
    return threads
