from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from token_window_planner.models import AuditReport, Finding
from token_window_planner.rules import RULES, SUBJECT_FIELDS, TEXT_FIELDS

SEVERITY_SCORE = {"low": 1, "medium": 3, "high": 5}
FAIL_LEVELS = {"low": 1, "medium": 3, "high": 5}


def read_records(path: Path, input_format: str = "auto") -> list[dict[str, Any]]:
    resolved = _resolve_format(path, input_format)
    if resolved == "text":
        return [
            {"line": index, "text": line.strip()}
            for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
            if line.strip()
        ]
    if resolved == "jsonl":
        return _read_jsonl(path)
    if resolved == "csv":
        return _read_csv(path)
    if resolved == "json":
        return _read_json(path)
    raise ValueError(f"unsupported input format: {resolved}")


def audit_records(records: list[dict[str, Any]]) -> AuditReport:
    findings: list[Finding] = []
    for index, record in enumerate(records, start=1):
        subject = _subject(record, index)
        haystack = _record_text(record)
        for rule in RULES:
            if re.search(rule.pattern, haystack, re.IGNORECASE | re.MULTILINE):
                findings.append(
                    Finding(
                        code=rule.code,
                        severity=rule.severity,
                        subject=subject,
                        message=rule.message,
                        recommendation=rule.recommendation,
                    )
                )
    score = sum(SEVERITY_SCORE[finding.severity] for finding in findings)
    return AuditReport(
        findings=tuple(findings),
        score=score,
        risk_level=_risk_level(score),
        records_scanned=len(records),
    )


def render_json(report: AuditReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown(report: AuditReport, title: str) -> str:
    lines = [
        f"# {title} report",
        "",
        f"Risk level: **{report.risk_level}**",
        f"Risk score: `{report.score}`",
        f"Records scanned: `{report.records_scanned}`",
        "",
        "## Findings",
        "",
    ]
    if report.findings:
        for finding in report.findings:
            lines.append(
                f"- **{finding.severity}** `{finding.code}` in "
                f"`{finding.subject}`: {finding.message}"
            )
            lines.append(f"  Recommendation: {finding.recommendation}")
    else:
        lines.append("- no findings")
    return "\n".join(lines) + "\n"


def should_fail(report: AuditReport, fail_on: str) -> bool:
    threshold = FAIL_LEVELS[fail_on]
    return any(SEVERITY_SCORE[finding.severity] >= threshold for finding in report.findings)


def _resolve_format(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".ndjson"}:
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    return "text"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        records.append(raw)
    return records


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV input requires a header row")
        return [dict(row) for row in reader]


def _read_json(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        if not all(isinstance(item, dict) for item in raw):
            raise ValueError("JSON list must contain objects")
        return raw
    if isinstance(raw, dict):
        return [raw]
    raise ValueError("JSON input must be an object or list of objects")


def _subject(record: dict[str, Any], index: int) -> str:
    for field in SUBJECT_FIELDS:
        value = record.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()
    if "line" in record:
        return f"line:{record['line']}"
    return str(index)


def _record_text(record: dict[str, Any]) -> str:
    parts = [str(value) for field in TEXT_FIELDS if (value := record.get(field))]
    if parts:
        return "\n".join(parts)
    return json.dumps(record, sort_keys=True, default=str)


def _risk_level(score: int) -> str:
    if score >= 8:
        return "high"
    if score >= 3:
        return "medium"
    return "low"
