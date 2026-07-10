"""Data models shared by lease backends."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LeaseRecord:
    """Backend representation of an active lease."""

    key: str
    owner_id: str
    expires_at: datetime
