# Evidence Court v0.1 Launch Packet

Use this page when publishing or asking someone to review/retweet the v0.1
launch. It is intentionally narrow: public copy should only use claims whose
listed local or remote gate has actually passed.

## One-Line Pitch

OpenMako Evidence Court checks whether a coding agent's final claim is backed
inside the supplied run record by reported files, reported commands, reported
test output, and scope boundaries.

## Retweet Copy

```text
Agents often say "done" or "tests passed".

OpenMako Evidence Court audits the supplied run record and flags missing
reported required tests, protected-file edits, out-of-scope changes, and
unsupported success claims.

It is not another coding agent. It is a claim-vs-evidence gate for supplied
agent-run records.
```

## Short Launch Copy

```text
I built OpenMako Evidence Court, a claim-vs-evidence gate for supplied agent-run records.

Agents often say "done" or "tests passed". Evidence Court checks the supplied
run record: what files were reported as read, what files were reported as
changed, what commands were reported, what test output was supplied, and whether
the edit stayed in scope.

Try:
  mako evidence-court --demo bad-run
  bash scripts/evidence_court_smoke.sh
  bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
```

## What The Demo Shows

- A bad run claims the calculator bug is fixed and tests pass.
- The evidence shows a protected test file was edited.
- The required pytest command was not reported.
- The verdict is `FAIL`.

## What Normal Tests Miss

Use this as the public explanation for why Evidence Court is useful even when
someone already has test output:

```text
Test output alone cannot tell whether the agent reported the required test,
edited protected tests, changed files outside scope, or made a final claim that
goes beyond the supplied evidence.

Evidence Court checks that gap in the supplied run record.
```

Boundary:

```text
Evidence Court does not prove tests really ran outside the supplied record.
It audits whether the record supports the claim.
```

The supplied CI-log path is narrower than arbitrary CI ingestion: it audits
supplied pytest logs, GitHub Actions test-step logs, or GitHub Actions job logs
only when a supported test command is visible and an explicit claim is provided.

## Proof Commands

Run these before public launch:

```bash
bash scripts/evidence_court_release_set.sh --check-staged-release-set
bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
python3 -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q
git diff --check
```

After the release commit and before remote publication:

```bash
bash scripts/evidence_court_release_set.sh --check-branch-diff origin/main
```

Expected local evidence:

- `bash scripts/evidence_court_smoke.sh` prints `Evidence Court smoke gate passed.`
- Focused release tests pass.
- Bad demo reports `Verdict: FAIL`.
- Good demo JSON reports `"verdict": "PASS"`.
- Marked transcript v0 fixture reports `"verdict": "FAIL"`.
- Supplied GitHub Actions pytest test-step log reports `"verdict": "PASS"`.
- Supplied failed pytest log reports `"verdict": "FAIL"`.
- Mixed JSON plus transcript inputs are rejected.
- `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke` writes the local reviewer artifact bundle.

## PR Checklist

Use this checklist as the PR description for the Evidence Court v0.1 release
candidate:

```markdown
## Evidence Court v0.1 Release

### Claim
- [ ] Public claim is limited to structured JSON run records, explicit marked
      transcript v0 files, explicit Evidence Court JSONL event streams, and
      supplied pytest/GitHub Actions logs with visible supported test commands.
- [ ] PR description does not claim native Claude/Codex/Cursor/Devin transcript
      ingestion or arbitrary CI ingestion.
- [ ] PR description does not claim broad SWE-style repair, unknown NPM
      reasoning, or Desktop L4/L5 autonomy.

### Included Files
- [ ] `.github/workflows/evidence-court.yml`
- [ ] `LICENSE`
- [ ] `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- [ ] `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`
- [ ] `docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md`
- [ ] `examples/evidence-court/bad-run.json`
- [ ] `examples/evidence-court/good-run.json`
- [ ] `MANIFEST.in`
- [ ] `pyproject.toml`
- [ ] `quantagent/__init__.py`
- [ ] `quantagent/evidence_court.py`
- [ ] `scripts/evidence_court_smoke.sh`
- [ ] `setup.py`
- [ ] `tests/fixtures/evidence_court/marked_bad_transcript.txt`
- [ ] `tests/test_evidence_court.py`
- [ ] `tests/test_evidence_court_smoke_script.py`

### Excluded From This Claim
- [ ] `quantagent/agent_planner.py`
- [ ] `quantagent/cli.py`
- [ ] `tests/test_agent_planner_contract.py`
- [ ] `tests/test_external_benchmark_multimodule_regression.py`

### Local Evidence
- [ ] `bash scripts/evidence_court_release_set.sh --check-staged-release-set`
- [ ] `bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy`
- [ ] `bash scripts/evidence_court_smoke.sh`
- [ ] `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`
- [ ] `python3 -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q`
- [ ] `git diff --check`
- [ ] After the release commit: `bash scripts/evidence_court_release_set.sh --check-branch-diff origin/main`

### Local Artifact Review Path
Before remote CI exists:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json
sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md
sed -n '1,40p' /tmp/evidence-court-smoke/bad-run.md
```

### Remote Evidence
- [ ] GitHub Actions `Evidence Court Smoke` is green for the PR head commit.
- [ ] GitHub Actions uploaded the `evidence-court-smoke` artifact containing
      `artifact-manifest.json`, `reviewer-quickstart.md`, `bad-run.md`,
      `fail-on-fail.json`, `good-run.json`, `marked-transcript.json`,
      `jsonl-events.json`, `openmako-agent-result.json`,
      `github-actions-test-step.log`, `github-actions-test-step.json`,
      `github-actions-job-log.log`, `github-actions-job-log.json`,
      `failed-pytest-log.log`, `failed-pytest-log.json`,
      `mixed-source-rejection.txt`, and `smoke-summary.txt`.
- [ ] Artifact content check: `artifact-manifest.json` lists the safe claim,
      review path, expected checks, source provenance checks, artifact file SHA-256 hashes, and boundaries; `reviewer-quickstart.md` tells reviewers to
      open `bad-run.md` first; `bad-run.md` shows `Verdict: FAIL`;
      `fail-on-fail.json` contains `"verdict": "FAIL"` and is
      written only after `--fail-on fail` exits 1; `good-run.json` shows `"verdict": "PASS"`;
      `marked-transcript.json` shows `"verdict": "FAIL"`; `jsonl-events.json` shows `"verdict": "FAIL"`;
      `openmako-agent-result.json` shows `"verdict": "FAIL"`;
      `github-actions-test-step.json` shows `"verdict": "PASS"`;
      `github-actions-job-log.json` shows `"verdict": "PASS"`;
      `failed-pytest-log.json` shows `"verdict": "FAIL"`;
      `mixed-source-rejection.txt` shows `exit_code=2`; report artifacts include `source: ...`;
      `artifact-manifest.json` includes SHA-256 hashes for every file in the review path;
      `smoke-summary.txt` shows
      `Evidence Court smoke gate passed.`
```

The PR body must include the same 30-second reviewer path as the remote
artifact: `bad-run.md`, `fail-on-fail.json`, `artifact-manifest.json`,
`reviewer-quickstart.md`, `jsonl-events.json`,
`github-actions-test-step.json`, `github-actions-job-log.json`,
`failed-pytest-log.json`, and
`mixed-source-rejection.txt`.

Optional remote artifact download, only if GitHub CLI is installed and
authenticated:

```bash
gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke
ls /tmp/evidence-court-smoke
sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json
sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md
sed -n '1,40p' /tmp/evidence-court-smoke/bad-run.md
```

## Safe Boundaries

Say:

- "Evidence Court audits supplied structured JSON run records, explicit marked
  transcript v0 files, and explicit Evidence Court JSONL event streams."
- "Marked transcript v0 is an explicit marker format."
- "Supplied pytest/GitHub Actions logs are audited only when a supported test
  command is visible."
- "The smoke gate is wired into GitHub Actions."
- "Remote CI evidence requires GitHub Actions `Evidence Court Smoke` green for the PR head commit."

Do not say:

- "Native Claude/Codex/Cursor/Devin ingestion is supported."
- "Arbitrary CI logs are ingested."
- "Evidence Court proves tests really ran outside the supplied record."
- "OpenMako proves broad SWE-style repository repair."
- "OpenMako has achieved Desktop L4/L5 autonomy."
- "The mocked JavaScript I/O benchmark proves real Node fs/process handling."

## Reviewer Ask

```text
Can you look at the narrow v0.1 claim?

The claim is not "another agent". It is: given a structured agent-run record,
OpenMako Evidence Court checks whether the final success claim is supported
inside the supplied record by reported files touched, reported commands,
reported test output, and scope boundaries.

The fastest review path is:
  mako evidence-court --demo bad-run
  bash scripts/evidence_court_smoke.sh
  bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
```

## Source Of Truth

- Release boundary: `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- Release file manifest: `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`
- Copyable PR body: `docs/EVIDENCE_COURT_V0_1_PR_BODY.md`
- Claim gates: `docs/CAPABILITY_GATES.md`
- Local release smoke: `bash scripts/evidence_court_smoke.sh`
- Local reviewer artifact bundle: `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`
- Local release set check: `bash scripts/evidence_court_release_set.sh --check`
- Strict staged release set check: `bash scripts/evidence_court_release_set.sh --check-staged-release-set`
- Remote smoke artifact contract, after a green PR workflow for the PR head
  commit: GitHub Actions `evidence-court-smoke`
- Workflow wiring: `.github/workflows/evidence-court.yml`
