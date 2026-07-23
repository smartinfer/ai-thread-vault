from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ImportedThread:
    id: str
    title: Optional[str] = None
    messages: List["ImportedMessage"] = field(default_factory=list)


@dataclass
class ImportedMessage:
    id: str
    thread_id: str
    role: str
    content: str
