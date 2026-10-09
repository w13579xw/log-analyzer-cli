import pytest

from loganalyzer.parser import LogEntry, parse_line, parse_lines


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "2026-10-08 10:15:30 INFO Server started",
            LogEntry("2026-10-08 10:15:30", "INFO", "Server started"),
        ),
        (
            "[2026-10-08T10:16:02] [error] Database unavailable",
            LogEntry("2026-10-08T10:16:02", "ERROR", "Database unavailable"),
        ),
        (
            "12:00:01 WARN: slow request",
            LogEntry("12:00:01", "WARN", "slow request"),
        ),
    ],
)
def test_parse_line_supported_formats(line, expected):
    assert parse_line(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",
        "server started successfully",
        "information: this line has no supported level",
    ],
)
def test_parse_line_ignores_unsupported_lines(line):
    assert parse_line(line) is None


def test_parse_line_strips_newline_and_delimiters():
    assert parse_line("12:00 [INFO] - ready\r\n") == LogEntry(
        "12:00", "INFO", "ready"
    )


def test_parse_lines_is_lazy_and_skips_unrecognized_lines():
    source = iter(["noise\n", "12:00 INFO started\n", "12:01 ERROR failed\n"])
    entries = parse_lines(source)
    assert next(entries) == LogEntry("12:00", "INFO", "started")
    assert next(entries) == LogEntry("12:01", "ERROR", "failed")
    with pytest.raises(StopIteration):
        next(entries)
