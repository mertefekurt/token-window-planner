import csv
import json

from token_window_planner.cli import main
from token_window_planner.core import audit_records, read_records, render_json, should_fail
from token_window_planner.rules import CLEAN_SAMPLE, HIGH_SAMPLE


def test_detects_high_risk_signal() -> None:
    report = audit_records([{"id": "case-1", "text": HIGH_SAMPLE}])

    assert report.risk_level in {"medium", "high"}
    assert any(finding.severity == "high" for finding in report.findings)


def test_clean_sample_has_no_findings() -> None:
    report = audit_records([{"id": "clean", "text": CLEAN_SAMPLE}])

    assert report.findings == ()
    assert report.score == 0


def test_reader_supports_csv(tmp_path) -> None:
    path = tmp_path / "input.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "text"])
        writer.writeheader()
        writer.writerow({"id": "row-1", "text": HIGH_SAMPLE})

    records = read_records(path)

    assert records[0]["id"] == "row-1"
    assert HIGH_SAMPLE in records[0]["text"]


def test_json_renderer_is_machine_readable() -> None:
    report = audit_records([{"id": "case-2", "text": HIGH_SAMPLE}])
    payload = json.loads(render_json(report))

    assert payload["records_scanned"] == 1
    assert payload["findings"][0]["severity"] == "high"


def test_fail_threshold_respects_clean_report() -> None:
    report = audit_records([{"id": "case-3", "text": CLEAN_SAMPLE}])

    assert not should_fail(report, "low")


def test_cli_json_exit_code(tmp_path, capsys) -> None:
    path = tmp_path / "input.txt"
    path.write_text(HIGH_SAMPLE, encoding="utf-8")

    exit_code = main([str(path), "--json", "--fail-on", "high"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert json.loads(captured.out)["findings"][0]["severity"] == "high"
