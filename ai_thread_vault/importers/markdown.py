import re
from pathlib import Path

from ai_thread_vault import ImportedThread, ImportedMessage


def parse(src: str) -> list[ImportedThread]:
    out: list[ImportedThread] = []
    for mp in sorted(Path(src).glob("*.md")):
        content = mp.read_text(encoding="utf-8")
        if "## " not in content:
            continue
        t = ImportedThread(id=mp.stem, title=mp.stem)
        parts = re.split(r"(?m)^##\s+(.+)$", content)
        i = 1
        while i + 1 < len(parts):
            role, body = parts[i].strip(), parts[i + 1].strip()
            if body:
                t.messages.append(ImportedMessage(
                    id=f"{mp.stem}-{i}", thread_id=mp.stem, role=role, content=body))
            i += 2
        out.append(t)
    return out
