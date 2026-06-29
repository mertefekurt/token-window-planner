from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Rule:
    code: str
    severity: str
    pattern: str
    message: str
    recommendation: str


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    subject: str
    message: str
    recommendation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "subject": self.subject,
            "message": self.message,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class AuditReport:
    findings: tuple[Finding, ...]
    score: int
    risk_level: str
    records_scanned: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "risk_level": self.risk_level,
            "records_scanned": self.records_scanned,
            "findings": [finding.to_dict() for finding in self.findings],
        }
