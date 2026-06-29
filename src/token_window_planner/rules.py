from __future__ import annotations

from token_window_planner.models import Rule

PROJECT_NAME = 'token-window-planner'
DESCRIPTION = 'Audit LLM prompt assembly plans for token budget and truncation risk.'
TEXT_FIELDS = ("text", "content", "description", "summary", "body", "notes", "message")
SUBJECT_FIELDS = ("id", "name", "service", "dataset", "route", "metric", "field", "path")
HIGH_SAMPLE = 'context_window 8192 input_tokens: 8100 reserved_output: 0 truncation: none'
MEDIUM_SAMPLE = '\\btruncation\\s*[:=]\\s*(none|missing|null)\\b'
CLEAN_SAMPLE = (
                   'context_window 8192 input_tokens 5200 reserved_output 1200 truncation ol'
                   'dest_context'
               )

RULES = (
    Rule(
        code='no-output-reserve',
        severity='high',
        pattern='\\breserved_output\\s*[:=]\\s*0\\b',
        message='no output token reserve is declared',
        recommendation='Reserve output tokens before adding context.',
    ),
    Rule(
        code='missing-truncation',
        severity='medium',
        pattern='\\btruncation\\s*[:=]\\s*(none|missing|null)\\b',
        message='truncation policy is missing',
        recommendation='Define deterministic truncation or retrieval cutoff behavior.',
    ),
    Rule(
        code='near-window-limit',
        severity='low',
        pattern='\\binput_tokens\\s*[:=]\\s*(8[0-9]{3}|9[0-9]{3}|1[0-9]{4})\\b',
        message='input token count is close to common context limits',
        recommendation='Add budget checks and telemetry before production.',
    ),
)
