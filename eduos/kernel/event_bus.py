from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[Event], None]]] = {}
        self.history: list[Event] = []

    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(event_name, []).append(handler)

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> Event:
        event = Event(event_name, payload or {})
        self.history.append(event)
        for handler in self._subscribers.get(event_name, []):
            handler(event)
        return event
