from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ClipboardItem:
    """Represents a single clipboard history entry captured from the system clipboard."""

    text: str
    app_origin: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
