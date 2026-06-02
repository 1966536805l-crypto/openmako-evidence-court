# Evidence Court v0.1 Release Cut

This checklist separates the Evidence Court v0.1 launch candidate from
unrelated Programming and planner experiments in the current worktree.

Use this before committing, opening a PR, or publishing a launch post.
The machine-checkable file boundary is
`docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`.

## Release Claim

Allowed claim:

```text
OpenMako Evidence Court v0.1 audits supplied structured JSON run records and
explicit marked transcript v0 files, and explicit Evidence Court JSONL event
streams, then reports claim evidence, scope
violations, test evidence from the supplied record, suspicious behavior, and
PASS/SUSPICIOUS/FAIL verdicts.
```

Do not claim native Claude Code, Codex, Cursor, Devin, GitHub Actions log, or CI
transcript ingestion. Marked transcript v0 is an explicit marker format, not a
vendor log parser.

## Include In Evidence Court v0.1

These files are part of the release candidate:

- `.github/workflows/evidence-court.yml`
- `LICENSE`
- `README.md`
- `pyproject.toml`
- `docs/CAPABILITY_GATES.md`
- `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`
- `docs/EVIDENCE_COURT_V0_1_PR_BODY.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`
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
- `examples/evidence-court/good-run.json`
- `quantagent/evidence_court.py`
- `quantagent/__init__.py`
- `quantagent/cli.py`
- `scripts/evidence_court_release_set.sh`
- `scripts/evidence_court_smoke.sh`
- `tests/fixtures/evidence_court/marked_bad_transcript.txt`
- `tests/test_evidence_court.py`
- `tests/test_evidence_court_smoke_script.py`

`PROGRESS.md` is not part of this public release set and is not evidence by
itself. Public claims must point to the smoke script, tests, examples, and CI
workflow above.

## Exclude From This Release Claim

These dirty files belong to the Programming/planner benchmark line and must not
be used to support the Evidence Court v0.1 launch claim:

- `quantagent/agent_planner.py`
- `tests/test_agent_planner_contract.py`
- `tests/test_external_benchmark_multimodule_regression.py`

They can ship in the same branch only if the release notes clearly separate
them from Evidence Court. They cannot justify claims such as broad SWE-style
repair, unknown NPM reasoning, or L4/L5 autonomy.

## Required Local Gate

Run:

```bash
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_release_set.sh --check
bash scripts/evidence_court_release_set.sh --check-branch-diff main
bash scripts/evidence_court_release_set.sh --check-staged-release-set
bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy
python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q
git diff --check
```

Expected evidence:

- bad demo renders `Verdict: FAIL`
- good demo JSON contains `"verdict": "PASS"`
- marked transcript fixture JSON contains `"verdict": "FAIL"`
- explicit JSONL event stream JSON contains `"verdict": "FAIL"`
- mixed `--input` plus `--from-transcript` plus `--from-jsonl-events` exits with code 2
- release-set verifier reports no staged excluded files
- branch-diff verifier reports the release branch diff is limited to Evidence
  Court v0.1 files
- strict release-set verifier reports every Evidence Court v0.1 release file is
  staged before commit
- staged claim-copy audit reports public copy keeps v0.1 boundaries
- README still says native Claude/Codex/Cursor/Devin/CI ingestion is not
  supported

## Required Remote Gate

After opening or updating the release PR, GitHub Actions must show
`Evidence Court Smoke` green for the PR head commit.
The run must upload an `evidence-court-smoke` artifact containing
`artifact-manifest.json`, `reviewer-quickstart.md`, `bad-run.md`,
`good-run.json`, `marked-transcript.json`, `jsonl-events.json`,
`mixed-source-rejection.txt`, and
`smoke-summary.txt`.

Artifact content check:

- `artifact-manifest.json` lists the safe claim, review path, expected checks,
  source provenance checks, and claim boundaries.
- `reviewer-quickstart.md` tells reviewers to open `bad-run.md` first and
  confirm `source: ...` in the generated reports.
- `bad-run.md` shows `Verdict: FAIL`.
- `good-run.json` contains `"verdict": "PASS"`.
- `marked-transcript.json` contains `"verdict": "FAIL"`.
- `jsonl-events.json` contains `"verdict": "FAIL"`.
- `mixed-source-rejection.txt` contains `exit_code=2`.
- report artifacts include `source: ...` in the Evidence section.
- `smoke-summary.txt` contains `Evidence Court smoke gate passed.`

Until that remote run exists, say "workflow wired locally" rather than "CI is
green".

Optional remote artifact download, only if GitHub CLI is installed and
authenticated:

```bash
gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke
ls /tmp/evidence-court-smoke
sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json
sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md
sed -n '1,40p' /tmp/evidence-court-smoke/bad-run.md
```

## Launch Copy Boundary

Safe short launch copy:

```text
I built OpenMako Evidence Court: a small audit gate for coding-agent runs.
Give it a structured run record or marked transcript v0 and it checks whether
the final claim is backed inside the supplied record by reported files touched,
reported commands, reported test output, and scope boundaries. Explicit
Evidence Court JSONL event streams are also supported.

Try:
  mako evidence-court --demo bad-run
  bash scripts/evidence_court_smoke.sh
```

Unsupported:

- native vendor transcript parsing
- CI log ingestion
- proof that tests actually ran outside the supplied record
- broad Programming repair ability
- desktop L4/L5 autonomy

Use `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md` for public launch copy. Do not
write new launch copy from memory.
