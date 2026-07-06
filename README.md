# Token Window Planner

![Token Window Planner cover](assets/readme-cover.svg)

> Audit LLM prompt assembly plans for token budget and truncation risk

![stack](https://img.shields.io/badge/stack-Python-16a34a?style=flat-square) ![python](https://img.shields.io/badge/python-3.11-dc2626?style=flat-square) ![license](https://img.shields.io/badge/license-MIT-7c3aed?style=flat-square) ![ci](https://img.shields.io/badge/ci-GitHub%20Actions-0891b2?style=flat-square)

## At a glance

| Area | Detail |
| --- | --- |
| Focus | context planning |
| Command | `token-window-planner` |
| Formats | text, JSON, JSONL, CSV |
| Output | Markdown table or JSON |

## What it checks

| Rule | Severity | What it catches |
| --- | --- | --- |
| `no-output-reserve` | high | no output token reserve is declared |
| `missing-truncation` | medium | truncation policy is missing |
| `near-window-limit` | low | input token count is close to common context limits |

## Try it locally

```bash
python -m pip install -e ".[dev]"
token-window-planner examples/sample.txt
token-window-planner examples/sample.txt --json --fail-on medium
```

## Notes from the code

`rules.py` keeps the project policy explicit, while `core.py` handles parsing and report rendering. The CLI stays thin on purpose so the checks are easy to test.

## Verify

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
python -m token_window_planner --help
```
