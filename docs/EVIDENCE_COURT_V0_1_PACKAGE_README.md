# OpenMako Evidence Court

Audit whether a coding agent's success claim is supported by a supplied run
record.

Evidence Court is a claim-vs-evidence gate. It checks what the supplied record
reports about files, commands, test output, scope boundaries, and final claims.

## Demo

```bash
mako evidence-court --demo bad-run
# Claim: Done. The calculator bug is fixed and tests pass.
# Evidence: edited protected path: tests/test_calculator.py
# Evidence: required test not run: python -m pytest tests/test_calculator.py -q
# Verdict: FAIL
```

To make CI or wrappers fail on a failing verdict:

```bash
mako evidence-court --demo bad-run --fail-on fail
```

## Supported In v0.1

- supplied structured JSON run records
- explicit marked transcript v0 files
- explicit Evidence Court JSONL event streams
- supplied pytest logs, GitHub Actions test-step logs, or GitHub Actions job
  logs with visible supported test commands
- JSON reports with `schema_version: "evidence-court.report.v0.1"`
- console aliases: `mako`, `openmako`, and `qagent`

## Boundary

Evidence Court v0.1 does not natively ingest Claude Code, Codex, Cursor, Devin,
or arbitrary CI logs. Its `--from-ci-log` path audits only supplied pytest logs,
GitHub Actions test-step logs, or GitHub Actions job logs with visible supported
test commands and an explicit claim. It does not prove tests really ran outside
the supplied record or supplied log. It does not claim broad repository repair
or desktop autonomy.

This package installs only the narrow package surface required by Evidence
Court: `quantagent.__init__` and `quantagent.evidence_court`.

## Inputs

Structured JSON:

```bash
mako evidence-court --input examples/evidence-court/bad-run.json
mako evidence-court --input examples/evidence-court/good-run.json --json
```

Marked transcript v0:

```bash
mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json
```

Explicit JSONL events:

```bash
mako evidence-court --from-jsonl-events run.events.jsonl --json
```

Supplied pytest/GitHub Actions log:

```bash
mako evidence-court --from-ci-log pytest.log --claim "Fixed. Tests pass." --required-test "python -m pytest tests/test_calculator.py -q" --json
```

## Review

Source repository:
https://github.com/1966536805l-crypto/openmako-evidence-court

Before treating a release candidate as public evidence, require a green
`Evidence Court Smoke` GitHub Actions run for the PR head commit and the
uploaded `evidence-court-smoke` artifact.
