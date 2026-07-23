from dataclasses import dataclass
from typing import Iterable, List

from . import ImportedMessage


_ROLE_MAP = {
    "human": "user",
    "person": "user",
    "bot": "assistant",
    "ai": "assistant",
    "model": "assistant",  # Gemini uses "model" for the assistant turn
    "sys": "system",
}

_CANONICAL_ROLES = {"user", "assistant", "system"}


@dataclass(frozen=True)
class CleanedMessage:
    id: str
    thread_id: str
    role: str
    content: str
    sequence: int



def _normalize_role(role: str) -> str:
    r = role.strip().lower()
    if r in _CANONICAL_ROLES:
        return r
    return _ROLE_MAP.get(r, "user")



def clean_thread(messages: Iterable[ImportedMessage]) -> List[CleanedMessage]:
    cleaned: List[CleanedMessage] = []
    seen = set()

    for message in messages:
        content = message.content
        if content.strip() == "":
            continue

        role = _normalize_role(message.role)
        dedup_key = (role, content)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        cleaned.append(
            CleanedMessage(
                id=message.id,
                thread_id=message.thread_id,
                role=role,
                content=content,
                sequence=len(cleaned) + 1,
            )
        )

    return cleaned
