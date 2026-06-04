# OpenMako Evidence Court

[![Evidence Court Smoke](https://github.com/1966536805l-crypto/openmako-evidence-court/actions/workflows/evidence-court.yml/badge.svg)](https://github.com/1966536805l-crypto/openmako-evidence-court/actions/workflows/evidence-court.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Agent Evidence Harness for coding agents.

Audit whether a coding agent's success claim is supported by a supplied run record. Evidence Court is an anti-fake-progress gate and claim-vs-evidence gate: it compares a final claim against the files, commands, test output, and scope reported in that record.

Agents often say "done", "fixed", or "tests passed" before the supplied record supports it. Evidence Court is not another coding agent, not a codegraph, not a token compressor, and not an agent skill library. It is a record auditor: given explicit run evidence, it reports whether the claim is supported.

Public proof: [docs/PUBLIC_PROOF.md](docs/PUBLIC_PROOF.md) binds the v0.1.2 claim to the tag, commit, smoke run, artifact digest, and 30-second reviewer path.
Public technical feedback can use the [technical review issue template](../../issues/new?template=technical-review-request.md); opening that issue is a request for boundary feedback, not evidence of endorsement.
Proof status and stale-proof boundaries are tracked in
[docs/CURRENT_PROOF_STATUS.md](docs/CURRENT_PROOF_STATUS.md).

Star this if you want a tiny CI-friendly gate that catches coding agents claiming "tests passed" without supplied evidence. Today: JSON records, OpenMako AgentRunResult JSON producer artifacts, marked transcript v0, and explicit JSONL events. Not claimed: native Claude/Codex/Cursor/CI log ingestion.

![OpenMako Evidence Court bad-run demo](docs/demo-terminal.svg)

## 10-Second Demo

```bash
mako evidence-court --demo bad-run
# CI gate: add --fail-on fail to exit 1 on FAIL
# Claim: Done. The calculator bug is fixed and tests pass.
# Evidence: edited protected path: tests/test_calculator.py
# Evidence: required test not run: python -m pytest tests/test_calculator.py -q
# Evidence: test output status reason: no known pass/fail pattern matched
# Verdict: FAIL
```

The bad demo is a supplied run record. This is the smallest evidence check: a bad supplied record says tests passed, but the record shows a protected test edit and no reported required pytest command.
To block CI on this verdict, run the same command with `--fail-on fail`; the bad run exits 1 instead of report-only 0.
Evidence Court does not inspect the real repository state or independently rerun tests. It checks whether the run record you supply contains enough evidence to support the final claim.
Current v0.1 reads JSON run records, OpenMako AgentRunResult JSON producer artifacts, explicit marked transcript v0 files, and explicit Evidence Court JSONL event streams. It does not parse raw chat transcripts or native Claude/Codex/Cursor/Devin/CI logs.

## What Normal Tests Miss

Test output alone does not answer whether an agent stayed honest about the run.
Evidence Court checks the supplied record for contradictions that ordinary test
output does not settle:
- did the run report the required test command, or only a weaker command?
- did it edit protected tests or out-of-scope files?
- did the final claim go beyond the supplied test evidence?

It does not prove tests really ran outside the supplied record. It audits
whether the supplied record supports the agent's claim.

For concrete examples, see
[what Evidence Court catches that normal tests miss](docs/EVIDENCE_COURT_COMPARISON.md).

## Quick Start

```bash
# From a checkout of this repository:
python3 -m pip install .
mako evidence-court --demo bad-run
```

`mako` is the primary CLI. `openmako` is an alias. `qagent` remains for compatibility. Default project is the current working directory.

For CI or wrappers, add `--fail-on fail` to return exit code 1 on `FAIL`, or
`--fail-on suspicious` to return exit code 1 on `FAIL` and `SUSPICIOUS`.
Without `--fail-on`, Evidence Court keeps the old report-only behavior and
returns 0 for completed audits.
To gate on one exact machine-readable category, repeat
`--fail-on-reason-code CODE`. For example, this exits 1 only when the supplied
record is missing the required test command:

```bash
mako evidence-court --input examples/evidence-court/bad-run.json --fail-on-reason-code test.required_not_run --json
```

To discover available exact reason-code gates:

```bash
mako evidence-court --list-reason-codes
mako evidence-court --list-reason-codes --json
```

## What It Checks

Evidence Court reports from the supplied record:
- Claim
- Evidence
- Scope violations
- Test evidence from the supplied record
- Structured test-output status and reason
- Suspicious behavior
- Machine-readable reason codes
- Verdict: PASS / SUSPICIOUS / FAIL

JSON reports include `schema_version: "evidence-court.report.v0.1"` so CI,
wrappers, and review tooling can check the report contract before reading
fields. `test_verification` includes both `test output status` and a
`test output status reason` line so reviewers can see the matched evidence
instead of trusting a black-box status word.
`test_output_status` and `test_output_status_reason` expose the same sampled
test-output classification as stable JSON fields for CI wrappers and review
bots that should not parse prose lines.
`reason_codes` gives CI wrappers stable categories such as
`test.required_not_run`, `scope.protected_path_edited`, and
`suspicious.success_claim_without_test_evidence` without parsing prose strings.

Machine-readable bad-run excerpt from `mako evidence-court --demo bad-run --json`
(excerpt, not the full report):

```json
{
  "schema_version": "evidence-court.report.v0.1",
  "verdict": "FAIL",
  "test_verification": [
    "required test not run: python -m pytest tests/test_calculator.py -q",
    "no test command observed",
    "test output status: unknown",
    "test output status reason: no known pass/fail pattern matched"
  ]
}
```

Full generated report fixture:
[`examples/evidence-court/bad-run.report.json`](examples/evidence-court/bad-run.report.json).

Try the same path with example records:

```bash
mako evidence-court --input examples/evidence-court/bad-run.json
mako evidence-court --input examples/evidence-court/good-run.json
mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json
```

Use the [redaction guide](docs/REDACTION_GUIDE.md) before turning a private
coding-agent run into a public supplied-record fixture.

## JSON Run Record

Current v0.1 supports structured JSON run records:

Adapter authors can start from the permissive schema at
[`examples/evidence-court/run-record.schema.json`](examples/evidence-court/run-record.schema.json).
It documents the explicit supplied-record fields that the v0.1 loader reads,
including command-object forms and aliases such as `claim`, `allowed_files`, and
`required_commands`. It is not a native vendor-log schema.

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
| `required_tests` / `required_commands` | Optional commands that must appear in the run |
| `source` | Optional source label for the run record |

It does not yet natively ingest Claude Code, Codex, Cursor, Devin, or CI logs. Those adapters need separate parsers before the project can claim native support.
Test-output status uses corpus-backed patterns for sampled pytest, Jest, Go test, unittest, Vitest, Mocha, Cargo, Maven, and Gradle outputs. This is sampled runner output support, not a universal test-runner or CI-log parser.

## OpenMako AgentRunResult

OpenMako producers can supply the explicit AgentRunResult JSON shape:

```bash
mako evidence-court --from-openmako-agent-run-result tests/fixtures/evidence_court/openmako_agent_run_result_bad.json --json
```

The fixture intentionally fails: the final claim says tests pass, but the
supplied artifact only reports `py_compile`, edits a protected test path, and
omits the required pytest command. This path requires
`"schema": "openmako.agent_run_result.v0"`.
It is not native Claude/Codex/Cursor/Devin/CI log parsing.

## Marked Transcript v0

Evidence Court can also convert an explicitly marked transcript into the same run-record model:

```bash
mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json
```

Marked transcript v0 uses `[section]...[/section]` blocks. Use
`[required_tests]` or `[required_commands]` for required test-command evidence.
It is not native vendor log parsing.

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

## Smoke Gate

Before making a public Evidence Court claim, run:

```bash
bash scripts/evidence_court_smoke.sh
```

To write the local reviewer artifact bundle:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
```

The smoke gate compiles the Evidence Court entry points, runs the focused test file, checks bad/good demo verdicts, checks marked transcript failure, rejects mixed evidence sources, and verifies that README still states the native-ingestion boundary.
The same gate is wired into GitHub Actions at `.github/workflows/evidence-court.yml`.
The release-cut boundary is tracked in `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`.
Launch copy is tracked in `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`.

## Review In 30 Seconds

1. Check the safe claim: Evidence Court audits supplied run records; it does
   not prove real test execution outside the supplied record.
2. Run `mako evidence-court --demo bad-run`; expected visible result:
   `Verdict: FAIL`.
3. For current local evidence, run
   `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`
   and open `/tmp/evidence-court-smoke/reviewer-quickstart.md`.
4. For public remote evidence, open
   [docs/CURRENT_PROOF_STATUS.md](docs/CURRENT_PROOF_STATUS.md) before trusting
   a smoke-run claim.
5. After a green PR-head GitHub Actions run, download the
   `evidence-court-smoke` artifact and open `reviewer-quickstart.md`.

Until that PR-head remote run exists, use the local smoke gate above; do not
claim remote CI evidence, external review, endorsement, share, or major-star
milestones.

## Launch Assets

- [public proof card](docs/PUBLIC_PROOF.md)
- [proof status and stale-proof boundary](docs/CURRENT_PROOF_STATUS.md)
- [terminal demo visual](docs/demo-terminal.svg)
- [v0.1.2 release notes](docs/RELEASE_NOTES_V0_1_2.md)
- [expert review brief](docs/EXPERT_REVIEW_BRIEF.md)
- [normal-tests comparison](docs/EVIDENCE_COURT_COMPARISON.md)
- [run-record field checklist](docs/RUN_RECORD_FIELD_CHECKLIST.md)
- [redaction guide](docs/REDACTION_GUIDE.md)
- [outreach templates](docs/OUTREACH.md)
- [outreach target tracker](docs/OUTREACH_TARGETS.md)
- [technical review request](docs/TECHNICAL_REVIEW_REQUEST.md)
- [technical review issue draft](docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md)
- [technical review issue template](../../issues/new?template=technical-review-request.md)
- [copyable launch post](docs/LAUNCH_POST.md)
- [social card](docs/social-card.svg)

## Boundaries

This public repository contains the Evidence Court v0.1 release set only. It does not ship or claim the broader OpenMako agent runtime, planner, desktop automation, quant trading readiness, or native Claude/Codex/Cursor/Devin/CI log ingestion.

Use `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md` as the file boundary for public claims.
