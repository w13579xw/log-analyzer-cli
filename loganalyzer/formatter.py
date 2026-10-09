"""Console and file formatting for parsed log entries and summaries."""

from collections import Counter
import csv
import json
from typing import Any, IO, Iterable, List, Optional

from .parser import LogEntry


def _cell(value: str, width: int) -> str:
    value = value.replace("|", "\\|")
    if len(value) > width:
        value = value[: width - 3] + "..."
    return value.ljust(width)


def format_table(entries: Iterable[LogEntry]) -> str:
    rows: List[LogEntry] = list(entries)
    widths = (19, 5, 60)
    header = ("TIMESTAMP", "LEVEL", "MESSAGE")
    lines = [
        f"| {_cell(header[0], widths[0])} | {_cell(header[1], widths[1])} | {_cell(header[2], widths[2])} |",
        f"+-{'-' * widths[0]}-+-{'-' * widths[1]}-+-{'-' * widths[2]}-+",
    ]
    for entry in rows:
        lines.append(
            f"| {_cell(entry.timestamp, widths[0])} | "
            f"{_cell(entry.level, widths[1])} | {_cell(entry.message, widths[2])} |"
        )
    return "\n".join(lines)


def format_summary(entries: Iterable[LogEntry]) -> str:
    counts = Counter(entry.level for entry in entries)
    total = sum(counts.values())
    return (
        f"Summary: {total} matching entr{'y' if total == 1 else 'ies'} "
        f"(INFO: {counts['INFO']}, WARN: {counts['WARN']}, ERROR: {counts['ERROR']})"
    )


def format_entry(entry: LogEntry) -> str:
    """Format one entry as a table row."""
    widths = (19, 5, 60)
    return (
        f"| {_cell(entry.timestamp, widths[0])} | "
        f"{_cell(entry.level, widths[1])} | {_cell(entry.message, widths[2])} |"
    )


def table_header() -> str:
    widths = (19, 5, 60)
    return "\n".join(
        (
            f"| {_cell('TIMESTAMP', widths[0])} | {_cell('LEVEL', widths[1])} | "
            f"{_cell('MESSAGE', widths[2])} |",
            f"+-{'-' * widths[0]}-+-{'-' * widths[1]}-+-{'-' * widths[2]}-+",
        )
    )


def write_json(entries: Iterable[LogEntry], output: IO[str]) -> None:
    """Write entries as a JSON array without collecting all entries."""
    output.write("[")
    first = True
    for entry in entries:
        if not first:
            output.write(",")
        json.dump(
            {
                "timestamp": entry.timestamp,
                "level": entry.level,
                "message": entry.message,
            },
            output,
            ensure_ascii=False,
        )
        first = False
    output.write("]\n")


def write_csv(entries: Iterable[LogEntry], output: IO[str]) -> None:
    """Write entries as CSV rows without collecting all entries."""
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("timestamp", "level", "message"))
    for entry in entries:
        writer.writerow((entry.timestamp, entry.level, entry.message))


class StreamingExporter:
    """Write one entry at a time in the selected file format."""

    def __init__(self, output: IO[str], output_format: str) -> None:
        self.output = output
        self.output_format = output_format
        self._first_json = True
        self._csv_writer: Optional[Any] = None

        if output_format == "json":
            output.write("[")
        elif output_format == "csv":
            self._csv_writer = csv.writer(output, lineterminator="\n")
            self._csv_writer.writerow(("timestamp", "level", "message"))
        else:
            raise ValueError(f"unsupported output format: {output_format}")

    def write(self, entry: LogEntry) -> None:
        if self.output_format == "json":
            if not self._first_json:
                self.output.write(",")
            json.dump(
                {
                    "timestamp": entry.timestamp,
                    "level": entry.level,
                    "message": entry.message,
                },
                self.output,
                ensure_ascii=False,
            )
            self._first_json = False
        else:
            assert self._csv_writer is not None
            self._csv_writer.writerow(
                (entry.timestamp, entry.level, entry.message)
            )

    def close(self) -> None:
        if self.output_format == "json":
            self.output.write("]\n")
