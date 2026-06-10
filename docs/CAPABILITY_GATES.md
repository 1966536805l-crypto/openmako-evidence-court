# OpenMako Capability Gates

This is a claim-promotion index, not another roadmap.

Its job is to prevent the Evidence Court launch hook from replacing the two
core agent capability lines: programming and autonomy. Public claims must stay
behind evidence, and unsupported surfaces must stay marked unsupported.

## Operating Rule

Use fast, narrow slices with hard evidence gates.

The project should not choose between "slow high quality" and "fast low
quality" as a global strategy. The rule is:

- Move fast on small vertical slices.
- Give every slice one runnable proof.
- Keep broad surfaces explicitly unsupported until their gate passes.
- Raise quality on the same slice before widening the claim.
- Let public README and release-note claims lag behind tests and artifacts.

Broad low-quality features are not acceptable for Programming or Autonomy.
Evidence Court can be a fast launch wedge only because its v0.1 boundary is
narrow and testable.

## Claim Promotion Matrix

| Capability claim | Current status | Promotion gate | Required evidence | Owner docs | Not solved yet |
| --- | --- | --- | --- | --- | --- |
| Evidence Court audits supplied structured JSON agent-run records | v0.1 narrow support | Bad demo fails, good demo passes, fake test commands are rejected, raw non-JSON input is rejected | `.github/workflows/evidence-court.yml`; `bash scripts/evidence_court_smoke.sh`; `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`; `py_compile quantagent/evidence_court.py tests/test_evidence_court.py`; `pytest tests/test_evidence_court.py`; package install smoke for `mako`/`openmako`/`qagent`; `mako evidence-court --demo bad-run`; `mako evidence-court --demo good-run --json` | [README.md](../README.md), [EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md](EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md) | Native Claude/Codex/Cursor/Devin transcript ingestion and arbitrary CI ingestion |
| Marked transcript v0 conversion | Candidate narrow adapter | Explicit `[section]...[/section]` fixture converts into `EvidenceCourtRun`, mixed input modes are rejected, and missing test output fails closed | `pytest tests/test_evidence_court.py`; `mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json`; mixed `--input` plus `--from-transcript` returns code 2 | [README.md](../README.md), [EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md](EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md) | Native vendor transcript parsing, duplicate/unclosed marker hardening, broad path normalization |
| Explicit Evidence Court JSONL event streams | Candidate narrow adapter | Explicit JSONL event fixture converts into `EvidenceCourtRun`, JSONL bad event stream fails closed, mixed JSON plus transcript plus JSONL input modes are rejected | `pytest tests/test_evidence_court.py`; `mako evidence-court --from-jsonl-events run.events.jsonl --json`; smoke artifact `jsonl-events.json` contains `"verdict": "FAIL"` | [README.md](../README.md), [EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md](EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md) | Native vendor transcript parsing, arbitrary CI ingestion, automatic event extraction |
| Supplied pytest/GitHub Actions log auditing | v0.1 narrow support, not native CI ingestion | Parser accepts only supplied pytest logs, GitHub Actions test-step logs, or GitHub Actions job logs with a visible supported test command and an explicit `--claim`; GitHub Actions `Run ...` groups are recognized; multi-line pytest commands are joined; missing command, missing claim, and GitHub Actions error markers fail closed | `pytest tests/test_evidence_court.py`; `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`; smoke artifacts `github-actions-test-step.json`, `github-actions-job-log.json`, and `failed-pytest-log.json`; `mako evidence-court --from-ci-log pytest.log --claim "Fixed. Tests pass." --required-test "python -m pytest tests/test_calculator.py -q" --json` | [README.md](../README.md), [EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md](EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md) | Native Claude/Codex/Cursor/Devin transcript parsing, arbitrary CI logs, proof that tests ran outside the supplied log |
| Programming evidence line | Separate from Evidence Court v0.1 | Less-pinned or real I/O-boundary package benchmark with hidden variants, repeats, exact patch scope, protected tests, and failure classes | Focused benchmark pytest; no-learning or no-seed baseline; approved-learning success; repeat stability >= 3; anti-cheat rejected; `git diff --check` | Separate gate docs outside this v0.1 release set | Broad unknown NPM/SWE-style repository repair |
| Autonomous code repair loop | Separate from Evidence Court v0.1 | Canonical `run_agent_loop` positive and negative repair coverage for plan, implement/refuse, post-edit verification, trajectory/query events, final claim guard, and stop-rule behavior | Positive repair test; negative missing/failed verification test; query event terminal `stop` or `stop_failure`; trajectory artifact; second unsafe edit blocked before disk write; direct CLI and agent-v3 compatibility coverage | Separate gate docs outside this v0.1 release set | Commit/mainline integration, remote CI artifact evidence, full related or full-suite proof, and broad unattended autonomy remain unproven |
| Desktop L4/L5 autonomy | Not claimed | L4/L5 eval gates pass with real execution, recovery, crash/misoperation metrics, and autopsy artifacts | `mako desktop-eval` report with execution gates, metrics, recovery evidence, and reviewed side-effect permissions | Separate gate docs outside this v0.1 release set | Reliable long-running multi-app autonomy |
| Quant live readiness | Gated, not implied by research readiness | Execution evidence gate passes with broker/tick/fill/slippage/capacity artifacts | `quant execution-gate` artifacts with hashes and schema checks; answer guard blocks live claims when `live_ready=false` | Separate gate docs outside this v0.1 release set; [README.md](../README.md) | Live trading evidence without broker-grade artifacts |

## Public Wording Rules

Allowed wording:

- "Evidence Court v0.1 audits supplied structured JSON run records."
- "Marked transcript v0 is an explicit marker format, not native vendor log
  parsing."
- "Supplied pytest/GitHub Actions logs are audited only when they include a
  visible supported test command and an explicit claim."
- "Programming evidence is tracked separately; do not use it to support the
  Evidence Court v0.1 launch claim."
- "Autonomy foundations exist, but broad autonomous worker reliability is not
  proven."
- "Desktop L4/L5, native agent transcript ingestion, and arbitrary CI ingestion
  are future gated work."

Forbidden wording until the matching gate passes:

- "Native Claude/Codex/Cursor/Devin ingestion is supported."
- "OpenMako proves broad SWE-style repository repair."
- "General unknown NPM package reasoning is proven."
- "Desktop L4/L5 autonomy is achieved."
- "Agents can safely run unattended overnight."
- "Evidence Court proves tests ran in the real world." It can only judge the
  supplied structured record, supplied pytest log, or supplied GitHub Actions
  log.

## Next Highest-Leverage Gates

1. Evidence Court release smoke: run `bash scripts/evidence_court_smoke.sh` locally
   and `.github/workflows/evidence-court.yml` in CI. The gate checks compile,
   focused test, bad demo FAIL, good demo PASS, marked transcript FAIL,
   mixed-input rejection, and README limitation wording.
2. Programming gate: a less-pinned or real I/O-boundary JavaScript package
   benchmark with the same no-learning, approved-learning, repeat, patch-scope,
   and anti-cheat checks already used for stronger evidence.
3. Autonomy gate: keep the canonical `run_agent_loop`, direct CLI, and
   agent-v3 stop-rule fixtures green, then commit a clean branch and verify
   remote CI artifacts before making broader autonomy claims.

## Release Rule

For every public-facing claim, include:

- What changed.
- What command or artifact proves it.
- What failure mode it reduces.
- What it does not solve.
- The next measurable gate.

If one of those lines is missing, the claim is not ready for public launch.
