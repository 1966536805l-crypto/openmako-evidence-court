# Evidence Court v0.1 Release Manifest

This manifest is the machine-checkable file boundary for the Evidence Court v0.1 public claim.
Use it before staging, committing, opening a PR, or publishing launch copy.
Evidence Court v0.1 is not a vendor log parser.

## Public Claim Boundary

Evidence Court v0.1 may claim support for:

- supplied structured JSON run records
- explicit marked transcript v0 files
- explicit Evidence Court JSONL event streams
- claim/evidence/scope/test/suspicion/verdict reporting from the supplied record
- JSON report schema marker `evidence-court.report.v0.1`
- local smoke gate and focused regression tests
- GitHub Actions workflow wiring

Evidence Court v0.1 must not claim support for:

- native Claude/Codex/Cursor/Devin transcript ingestion
- GitHub Actions or CI log ingestion
- proof that tests actually ran outside the supplied record
- broad SWE-style repository repair
- unknown NPM package reasoning
- Desktop L4/L5 autonomy
- real Node fs/process handling from mocked JavaScript I/O benchmarks

## Include

Only these release files support the Evidence Court v0.1 public claim:

- `.github/ISSUE_TEMPLATE/technical-review-request.md`
- `.github/workflows/evidence-court.yml`
- `LICENSE`
- `README.md`
- `pyproject.toml`
- `docs/CAPABILITY_GATES.md`
- `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`
- `docs/EVIDENCE_COURT_V0_1_PR_BODY.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`
- `docs/EVIDENCE_COURT_COMPARISON.md`
- `docs/REDACTION_GUIDE.md`
- `docs/CURRENT_PROOF_STATUS.md`
- `docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md`
- `docs/EXPERT_REVIEW_BRIEF.md`
- `docs/OUTREACH.md`
- `docs/OUTREACH_TARGETS.md`
- `docs/TECHNICAL_REVIEW_REQUEST.md`
- `docs/PUBLIC_PROOF.md`
- `docs/demo-terminal.svg`
- `docs/LAUNCH_POST.md`
- `docs/social-card.svg`
- `docs/RELEASE_NOTES_V0_1_0.md`
- `docs/RELEASE_NOTES_V0_1_1.md`
- `docs/RELEASE_NOTES_V0_1_2.md`
- `examples/evidence-court/bad-run.json`
- `examples/evidence-court/bad-run.report.json`
- `examples/evidence-court/good-run.json`
- `examples/evidence-court/redacted-real-world-bad-run.json`
- `quantagent/evidence_court.py`
- `quantagent/__init__.py`
- `quantagent/cli.py`
- `scripts/evidence_court_release_set.sh`
- `scripts/evidence_court_smoke.sh`
- `tests/fixtures/evidence_court/marked_bad_transcript.txt`
- `tests/fixtures/evidence_court/openmako_agent_run_result_bad.json`
- `tests/fixtures/evidence_court/test_outputs/runner_outputs.json`
- `tests/test_evidence_court.py`
- `tests/test_evidence_court_smoke_script.py`

`PROGRESS.md` is not part of this public release set and is not release
evidence by itself.

## Exclude

These current dirty files belong to the Programming/planner benchmark line and
must not support the Evidence Court v0.1 public claim:

- `quantagent/agent_planner.py`
- `tests/test_agent_planner_contract.py`
- `tests/test_external_benchmark_multimodule_regression.py`

If they ship in the same branch, PR text and launch copy must keep them outside
the Evidence Court claim.

## Required Gate

Run before release:

```bash
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --check
bash scripts/evidence_court_release_set.sh --check-branch-diff main
bash scripts/evidence_court_release_set.sh --check-staged-release-set
bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q
git diff --check
```

After opening or updating the release PR, remote GitHub Actions must show
`Evidence Court Smoke` green for the PR head commit. Until then, say only
"workflow wired locally".
The remote run must upload the `evidence-court-smoke` artifact with
`artifact-manifest.json`, `reviewer-quickstart.md`, `bad-run.md`,
`redacted-real-world-bad-run.json`, `fail-on-fail.json`, `good-run.json`,
`marked-transcript.json`, `jsonl-events.json`, `mixed-source-rejection.txt`,
and `smoke-summary.txt`.

Artifact content check:

- `artifact-manifest.json` lists the safe claim, generated files, expected
  checks, source provenance checks, artifact file SHA-256 hashes, and
  boundaries.
- `reviewer-quickstart.md` tells reviewers to open `bad-run.md` first and
  confirm `source: ...` in the generated reports.
- `bad-run.md` shows `Verdict: FAIL`.
- `bad-run.report.json` is a full generated JSON report fixture for
  `examples/evidence-court/bad-run.json` and contains
  `"schema_version": "evidence-court.report.v0.1"` and `"verdict": "FAIL"`.
- `redacted-real-world-bad-run.json` contains `"verdict": "FAIL"` and
  `source: examples/evidence-court/redacted-real-world-bad-run.json`.
- `fail-on-fail.json` contains `"verdict": "FAIL"` and is written only after `--fail-on fail` exits 1.
- `good-run.json` contains `"verdict": "PASS"`.
- `marked-transcript.json` contains `"verdict": "FAIL"`.
- `jsonl-events.json` contains `"verdict": "FAIL"`.
- `mixed-source-rejection.txt` contains `exit_code=2`.
- report artifacts include `source: ...` in the Evidence section.
- `artifact-manifest.json` includes SHA-256 hashes for every file in the review
  path.
- `smoke-summary.txt` contains `Evidence Court smoke gate passed.`
- `bash scripts/evidence_court_release_set.sh --verify-artifact-dir <artifact-dir>`
  verifies the artifact file set, manifest contract, artifact SHA-256 hashes,
  expected verdicts, source provenance, and boundary text.

The PR body must include the same 30-second reviewer path: `bad-run.md`,
`redacted-real-world-bad-run.json`, `fail-on-fail.json`,
`artifact-manifest.json`, `reviewer-quickstart.md`, `jsonl-events.json`, and
`mixed-source-rejection.txt`.

Optional remote artifact download, only if GitHub CLI is installed and
authenticated:

```bash
gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
ls /tmp/evidence-court-smoke
sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json
sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md
sed -n '1,40p' /tmp/evidence-court-smoke/bad-run.md
```
