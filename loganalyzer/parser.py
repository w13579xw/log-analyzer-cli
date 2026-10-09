"""Parsing for common server log lines."""

from dataclasses import dataclass
import re
from typing import Iterable, Iterator, Optional


_LEVEL_PATTERN = re.compile(r"\b(INFO|WARN|ERROR)\b", re.IGNORECASE)


@dataclass(frozen=True)
class LogEntry:
    timestamp: str
    level: str
    message: str


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse a line containing a supported level; return None for other lines."""
    match = _LEVEL_PATTERN.search(line)
    if not match:
        return None

    before_level = line[: match.start()].strip()
    timestamp = before_level.strip("[] ")
    message = line[match.end() :].strip(" \t:-[]")
    return LogEntry(timestamp=timestamp, level=match.group(1).upper(), message=message)


def parse_lines(lines: Iterable[str]) -> Iterator[LogEntry]:
    for line in lines:
        entry = parse_line(line.rstrip("\r\n"))
        if entry is not None:
            yield entry
