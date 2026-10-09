"""Command-line interface for LogAnalyzer."""

import argparse
import sys
from pathlib import Path
from typing import IO, Iterator, Optional, Sequence, Set, Tuple

from .formatter import StreamingExporter, format_entry, table_header
from .parser import LogEntry, parse_lines


LEVELS = ("INFO", "WARN", "ERROR")
OUTPUT_FORMATS = ("json", "csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loganalyzer",
        description="Filter and summarize server log files.",
    )
    parser.add_argument("path", help="Path to the log file")
    parser.add_argument(
        "--level",
        action="append",
        choices=LEVELS,
        help="Only show this level; may be provided more than once",
    )
    parser.add_argument(
        "--output-format",
        choices=OUTPUT_FORMATS,
        help="Export matching entries as JSON or CSV",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Output file used with --output-format",
    )
    return parser


def _validate_input(path: Path) -> Optional[str]:
    if not path.exists():
        return f"loganalyzer: input file does not exist: '{path}'"
    if not path.is_file():
        return f"loganalyzer: input path is not a file: '{path}'"
    try:
        if path.stat().st_size == 0:
            return f"loganalyzer: input file is empty: '{path}'"
    except OSError as exc:
        return f"loganalyzer: cannot inspect '{path}': {exc}"
    return None


def _open_output(path: Path, output_format: str) -> IO[str]:
    newline = "" if output_format == "csv" else None
    return path.open("w", encoding="utf-8", newline=newline)


def _stream_entries(
    log_file: IO[str],
    selected_levels: Optional[Set[str]],
) -> Iterator[LogEntry]:
    for entry in parse_lines(log_file):
        if selected_levels is None or entry.level in selected_levels:
            yield entry


def _process_entries(
    entries: Iterator[LogEntry],
    output: IO[str],
    export_file: Optional[IO[str]],
    output_format: Optional[str],
) -> Tuple[int, int, int, int]:
    """Write output while iterating, returning total and per-level counts."""
    counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
    total = 0

    exporter = (
        StreamingExporter(export_file, output_format)
        if export_file is not None and output_format is not None
        else None
    )
    wrote_header = False
    for entry in entries:
        if not wrote_header:
            output.write(table_header())
            output.write("\n")
            wrote_header = True
        total += 1
        counts[entry.level] += 1
        output.write(format_entry(entry))
        output.write("\n")
        if exporter is not None:
            exporter.write(entry)

    if exporter is not None:
        exporter.close()
    return total, counts["INFO"], counts["WARN"], counts["ERROR"]


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.path)
    validation_error = _validate_input(path)
    if validation_error:
        print(validation_error, file=sys.stderr)
        return 1

    if args.output and not args.output_format:
        print("loganalyzer: --output requires --output-format", file=sys.stderr)
        return 2
    if args.output_format and not args.output:
        print("loganalyzer: --output-format requires --output FILE", file=sys.stderr)
        return 2

    selected = set(args.level) if args.level else None
    output_path = Path(args.output) if args.output else None
    if output_path is not None and output_path.resolve() == path.resolve():
        print(
            "loganalyzer: output file must be different from the input file",
            file=sys.stderr,
        )
        return 2
    export_file = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as log_file:
            if output_path is not None:
                export_file = _open_output(output_path, args.output_format)
            try:
                total, info, warn, error = _process_entries(
                    _stream_entries(log_file, selected),
                    sys.stdout,
                    export_file,
                    args.output_format,
                )
            finally:
                if export_file is not None:
                    export_file.close()
    except OSError as exc:
        print(f"loganalyzer: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except MemoryError:
        print(
            "loganalyzer: insufficient memory while processing the log stream",
            file=sys.stderr,
        )
        return 1

    if total == 0:
        print(
            f"loganalyzer: no supported log entries found in '{path}'",
            file=sys.stderr,
        )
        return 1

    print(
        f"Summary: {total} matching entr{'y' if total == 1 else 'ies'} "
        f"(INFO: {info}, WARN: {warn}, ERROR: {error})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
