"""Paper trail logger for tracking all agent work."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class LogEntry:
    phase: str
    agent: str
    timestamp: str
    data: dict


class PaperTrailLogger:
    """Accumulates a full paper trail of all agent work."""

    def __init__(self):
        self.entries: list[LogEntry] = []

    def log(self, phase: str, agent: str, data: dict) -> None:
        self.entries.append(
            LogEntry(
                phase=phase,
                agent=agent,
                timestamp=datetime.now(timezone.utc).isoformat(),
                data=data,
            )
        )

    def get_trail(self) -> list[dict]:
        return [
            {
                "phase": e.phase,
                "agent": e.agent,
                "timestamp": e.timestamp,
                "data": e.data,
            }
            for e in self.entries
        ]

    def get_phase(self, phase: str) -> list[dict]:
        return [
            {"agent": e.agent, "data": e.data}
            for e in self.entries
            if e.phase == phase
        ]
