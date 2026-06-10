# OpenMako Evidence Court

Audit whether a coding agent's success claim is supported by a supplied run record.

Agents often say "done", "fixed", or "tests passed" before the supplied record supports it. Evidence Court is not another coding agent; it is a claim-vs-evidence gate that checks whether the record reports the required files, commands, test output, and scope.

## 10-Second Demo

```bash
mako evidence-court --demo bad-run
# Claim: Done. The calculator bug is fixed and tests pass.
# Evidence: edited protected path: tests/test_calculator.py
# Evidence: required test not run: python -m pytest tests/test_calculator.py -q
# Verdict: FAIL
```

The bad demo is a supplied run record. This is the smallest evidence check: a bad supplied record says tests passed, but the record shows a protected test edit and no reported required pytest command.
To block CI on this verdict, run the same command with `--fail-on fail`; the bad run exits 1 instead of report-only 0.
Current v0.1 reads JSON run records, explicit marked transcript v0 files,
explicit Evidence Court JSONL event streams, and supplied pytest/GitHub Actions
test-step logs or supplied GitHub Actions job logs with a visible supported
test command. It does not parse raw chat transcripts, native
Claude/Codex/Cursor/Devin logs, or arbitrary CI logs.

For technical review of this v0.1 slice, start with
[`docs/EVIDENCE_COURT_V0_1_PR_BODY.md`](docs/EVIDENCE_COURT_V0_1_PR_BODY.md).
It keeps the Evidence Court claim separate from broader OpenMako autonomy and
planning work.
Broader OpenMako / QuantAgent capability evidence is intentionally outside this
Evidence Court v0.1 README. `docs/OPENMAKO_CAPABILITY_EVIDENCE.md` is
informative context only, not release evidence; do not use it to expand this
v0.1 claim.

## What Normal Tests Miss

Test output alone does not answer whether an agent stayed honest about the run.
Evidence Court checks the supplied record for contradictions that ordinary test
output does not settle:
- did the run report the required test command, or only a weaker command?
- did it edit protected tests or out-of-scope files?
- did the final claim go beyond the supplied test evidence?

It does not prove tests really ran outside the supplied record. It audits
whether the supplied record supports the agent's claim.

## Quick Start

```bash
# From a checkout of this repository:
python3 -m pip install -e .
mako evidence-court --demo bad-run
```

`mako` is the primary CLI. `openmako` is an alias. `qagent` remains for compatibility. Default project is the current working directory.

Packaging boundary: The open-mako wheel for this release installs only the
narrow quantagent package surface required by Evidence Court:
`quantagent.__init__` and `quantagent.evidence_court`. Broader OpenMako and
quantagent runtime modules are outside this launch claim unless covered by
separate gates.

For CI or wrappers, add `--fail-on fail` to return exit code 1 on `FAIL`, or
`--fail-on suspicious` to return exit code 1 on `FAIL` and `SUSPICIOUS`.
Without `--fail-on`, Evidence Court keeps the old report-only behavior and
returns 0 for completed audits.

## What It Checks

Evidence Court reports from the supplied record:
- Claim
- Evidence
- Scope violations
- Test evidence from the supplied record
- Suspicious behavior
- Verdict: PASS / SUSPICIOUS / FAIL

JSON reports include `schema_version: "evidence-court.report.v0.1"` so CI,
wrappers, and review tooling can check the report contract before reading
fields.

Try the same path with example records:

```bash
mako evidence-court --input examples/evidence-court/bad-run.json
mako evidence-court --input examples/evidence-court/good-run.json
```

## JSON Run Record

Current v0.1 supports structured JSON run records:

| Field | Meaning |
| --- | --- |
| `claimed_task` | What the agent was asked to do |
| `files_read` | Files the run says it inspected |
| `files_edited` | Files the run says it changed |
| `commands_run` | Commands the run says it executed |
| `test_output` | Captured test or command output |
| `final_claim` | The agent's final success claim |
| `allowed_edit_paths` | Optional expected edit scope |
| `protected_paths` | Optional paths that should not be changed |
| `required_tests` | Optional commands that must appear in the run |
| `source` | Optional source label for the run record |

It does not yet natively ingest Claude Code, Codex, Cursor, or Devin logs.
The CI-log path is intentionally narrower: it audits supplied pytest/GitHub
Actions test-step logs or supplied GitHub Actions job logs only when a supported
test command is visible and the caller provides an explicit `--claim`.

## Marked Transcript v0

Evidence Court can also convert an explicitly marked transcript into the same run-record model:

```bash
mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json
```

Marked transcript v0 uses `[section]...[/section]` blocks. It is not native vendor log parsing.

## Explicit JSONL Events

Line-oriented integrations can also supply explicit Evidence Court JSONL events:

```bash
cat > run.events.jsonl <<'JSONL'
{"event":"claimed_task","text":"Fix calculator.add; only calculator.py may be edited."}
{"event":"final_claim","text":"Done. The calculator bug is fixed and tests pass."}
{"event":"file_read","path":"calculator.py"}
{"event":"file_edit","path":"tests/test_calculator.py"}
{"event":"command","command":"python -m py_compile calculator.py"}
{"event":"required_test","command":"python -m pytest tests/test_calculator.py -q"}
JSONL
mako evidence-court --from-jsonl-events run.events.jsonl --json
```

This is an explicit Evidence Court event format for producers that already know
what they are reporting. It is not native Claude/Codex/Cursor/Devin/CI log parsing.

## Supplied CI Test Logs

Evidence Court can audit a supplied pytest log, GitHub Actions test-step log, or
GitHub Actions job log when the log contains a visible supported test command.
The caller must provide the claim being audited:

```bash
mako evidence-court \
  --from-ci-log pytest.log \
  --claim "Fixed. Tests pass." \
  --required-test "python -m pytest tests/test_calculator.py -q" \
  --json
```

This is not arbitrary CI ingestion and it does not prove the tests ran outside
the supplied log.

## Smoke Gate

Before making a public Evidence Court claim, run:

```bash
bash scripts/evidence_court_smoke.sh
```

To write the local reviewer artifact bundle:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
```

The smoke gate compiles the Evidence Court entry points, runs the focused test
file, checks bad/good demo verdicts, checks marked transcript failure, checks
supplied pytest/GitHub Actions test-step log PASS/FAIL artifacts, rejects mixed
evidence sources, checks a supplied GitHub Actions job-log artifact, and
verifies that README still states the native-ingestion boundary.
The same gate is wired into GitHub Actions at `.github/workflows/evidence-court.yml`.
The release-cut boundary is tracked in `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`.
Launch copy is tracked in `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`.

## Review In 30 Seconds

After a green PR-head GitHub Actions run, download the `evidence-court-smoke` artifact and open `reviewer-quickstart.md`.
Before remote CI exists, run `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke` and open `/tmp/evidence-court-smoke/reviewer-quickstart.md`.
Until that PR-head remote run exists, use the local smoke gate above; do not claim remote CI evidence.
