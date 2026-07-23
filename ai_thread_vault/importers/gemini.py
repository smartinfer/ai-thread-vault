import json
from pathlib import Path

from ai_thread_vault import ImportedThread, ImportedMessage


def parse(src: str) -> list[ImportedThread]:
    """Parse a Gemini (Google) conversation export.

    Assumed shape: a top-level list of conversations, or {"conversations": [...]},
    each with a title and a list of `messages` (or `turns`) whose role is "user"
    or "model" (Gemini's assistant role; mapped to "assistant" downstream).

    NOTE: validate against a real Google Takeout "Gemini Apps" export and adjust
    the field names if they differ — the shape here is the assumed contract.
    """
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    convs = data.get("conversations", []) if isinstance(data, dict) else data
    out: list[ImportedThread] = []
    for i, c in enumerate(convs):
        cid = str(c.get("id") or c.get("conversation_id") or f"gemini-{i}")
        thread = ImportedThread(id=cid, title=c.get("title"))
        for j, m in enumerate(c.get("messages") or c.get("turns") or []):
            role = m.get("role") or m.get("author") or "user"
            content = m.get("content") or m.get("text") or ""
            if content:
                thread.messages.append(
                    ImportedMessage(id=f"{cid}-{j}", thread_id=cid, role=role, content=content))
        out.append(thread)
    return out
