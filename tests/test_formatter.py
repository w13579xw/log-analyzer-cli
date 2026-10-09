import csv
import io
import json

from loganalyzer.formatter import (
    format_entry,
    format_summary,
    format_table,
    StreamingExporter,
    table_header,
    write_csv,
    write_json,
)
from loganalyzer.parser import LogEntry


ENTRIES = [
    LogEntry("12:00", "INFO", "started"),
    LogEntry("12:01", "WARN", "slow | request"),
    LogEntry("12:02", "ERROR", "failed"),
]


def test_format_table_contains_header_rows_and_escapes_pipe():
    result = format_table(ENTRIES)
    assert result.startswith(table_header())
    assert format_entry(ENTRIES[0]) in result
    assert r"slow \| request" in result


def test_format_table_handles_empty_input():
    result = format_table([])
    assert result == table_header()


def test_format_table_truncates_long_cells():
    result = format_entry(LogEntry("timestamp", "INFO", "x" * 100))
    assert "..." in result
    assert len(result.split("|")[3]) == 62


def test_format_summary_singular_and_plural():
    assert format_summary([ENTRIES[0]]) == (
        "Summary: 1 matching entry (INFO: 1, WARN: 0, ERROR: 0)"
    )
    assert format_summary(ENTRIES) == (
        "Summary: 3 matching entries (INFO: 1, WARN: 1, ERROR: 1)"
    )


def test_write_json_streams_valid_array():
    output = io.StringIO()
    write_json(iter(ENTRIES), output)
    assert json.loads(output.getvalue()) == [
        {"timestamp": "12:00", "level": "INFO", "message": "started"},
        {"timestamp": "12:01", "level": "WARN", "message": "slow | request"},
        {"timestamp": "12:02", "level": "ERROR", "message": "failed"},
    ]


def test_write_json_handles_empty_input():
    output = io.StringIO()
    write_json([], output)
    assert output.getvalue() == "[]\n"


def test_write_csv_streams_header_and_rows():
    output = io.StringIO()
    write_csv(iter(ENTRIES), output)
    rows = list(csv.reader(io.StringIO(output.getvalue())))
    assert rows == [
        ["timestamp", "level", "message"],
        ["12:00", "INFO", "started"],
        ["12:01", "WARN", "slow | request"],
        ["12:02", "ERROR", "failed"],
    ]


def test_write_csv_handles_empty_input():
    output = io.StringIO()
    write_csv([], output)
    assert output.getvalue() == "timestamp,level,message\n"


def test_streaming_exporter_writes_json_incrementally():
    output = io.StringIO()
    exporter = StreamingExporter(output, "json")
    exporter.write(ENTRIES[0])
    exporter.write(ENTRIES[1])
    exporter.close()
    assert json.loads(output.getvalue()) == [
        {"timestamp": "12:00", "level": "INFO", "message": "started"},
        {"timestamp": "12:01", "level": "WARN", "message": "slow | request"},
    ]


def test_streaming_exporter_writes_csv_incrementally():
    output = io.StringIO()
    exporter = StreamingExporter(output, "csv")
    exporter.write(ENTRIES[2])
    exporter.close()
    rows = list(csv.reader(io.StringIO(output.getvalue())))
    assert rows == [
        ["timestamp", "level", "message"],
        ["12:02", "ERROR", "failed"],
    ]
