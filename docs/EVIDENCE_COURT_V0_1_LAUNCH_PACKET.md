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

## Proof Commands

Run these before public launch:

```bash
bash scripts/evidence_court_release_set.sh --check-staged-release-set
bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q
git diff --check
```

After the release commit and before remote publication:

```bash
bash scripts/evidence_court_release_set.sh --check-branch-diff main
```

Expected local evidence:

- `bash scripts/evidence_court_smoke.sh` prints `Evidence Court smoke gate passed.`
- Focused release tests pass.
- Bad demo reports `Verdict: FAIL`.
- Good demo JSON reports `"verdict": "PASS"`.
- Marked transcript v0 fixture reports `"verdict": "FAIL"`.
- Mixed JSON plus transcript inputs are rejected.
- `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke` writes the local reviewer artifact bundle.

## PR Checklist

Use this checklist as the PR description for the Evidence Court v0.1 release
candidate:

```markdown
## Evidence Court v0.1 Release

### Claim
- [ ] Public claim is limited to structured JSON run records, explicit marked
      transcript v0 files, and explicit Evidence Court JSONL event streams.
- [ ] PR description does not claim native Claude/Codex/Cursor/Devin/CI log
      ingestion.
- [ ] PR description does not claim broad SWE-style repair, unknown NPM
      reasoning, or Desktop L4/L5 autonomy.

### Included Files
- [ ] `.github/workflows/evidence-court.yml`
- [ ] `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- [ ] `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`
- [ ] `docs/EVIDENCE_COURT_COMPARISON.md`
- [ ] `docs/REDACTION_GUIDE.md`
- [ ] `docs/CURRENT_PROOF_STATUS.md`
- [ ] `docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md`
- [ ] `examples/evidence-court/bad-run.json`
- [ ] `examples/evidence-court/good-run.json`
- [ ] `examples/evidence-court/redacted-real-world-bad-run.json`
- [ ] `quantagent/evidence_court.py`
- [ ] `scripts/evidence_court_smoke.sh`
- [ ] `tests/fixtures/evidence_court/marked_bad_transcript.txt`
- [ ] `tests/test_evidence_court.py`
- [ ] `tests/test_evidence_court_smoke_script.py`

### Excluded From This Claim
- [ ] `quantagent/agent_planner.py`
- [ ] `tests/test_agent_planner_contract.py`
- [ ] `tests/test_external_benchmark_multimodule_regression.py`

### Local Evidence
- [ ] `bash scripts/evidence_court_release_set.sh --check-staged-release-set`
- [ ] `bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy`
- [ ] `bash scripts/evidence_court_smoke.sh`
- [ ] `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`
- [ ] `python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q`
- [ ] `git diff --check`
- [ ] After the release commit: `bash scripts/evidence_court_release_set.sh --check-branch-diff main`

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
      `redacted-real-world-bad-run.json`, `fail-on-fail.json`,
      `good-run.json`, `marked-transcript.json`,
      `openmako-agent-run-result.json`, `jsonl-events.json`,
      `mixed-source-rejection.txt`, and `smoke-summary.txt`.
- [ ] Artifact content check: `artifact-manifest.json` lists the safe claim,
      review path, expected checks, source provenance checks, artifact file SHA-256 hashes, and boundaries; `reviewer-quickstart.md` tells reviewers to
      open `bad-run.md` first; `bad-run.md` shows `Verdict: FAIL`;
      `redacted-real-world-bad-run.json` shows `"verdict": "FAIL"` and
      `source: examples/evidence-court/redacted-real-world-bad-run.json`;
      `fail-on-fail.json` contains `"verdict": "FAIL"` and is
      written only after `--fail-on fail` exits 1; `good-run.json` shows `"verdict": "PASS"`;
      `marked-transcript.json` shows `"verdict": "FAIL"`; `openmako-agent-run-result.json`
      shows `"verdict": "FAIL"` with `source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json`;
      `jsonl-events.json` shows `"verdict": "FAIL"`;
      `mixed-source-rejection.txt` shows `exit_code=2`; report artifacts include `source: ...`;
      `artifact-manifest.json` includes SHA-256 hashes for every file in the review path;
      `smoke-summary.txt` shows
      `Evidence Court smoke gate passed.`
```

The PR body must include the same 30-second reviewer path as the remote
artifact: `bad-run.md`, `fail-on-fail.json`, `artifact-manifest.json`,
`redacted-real-world-bad-run.json`, `reviewer-quickstart.md`,
`openmako-agent-run-result.json`, `jsonl-events.json`, and
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

## Post-PR Public Gate

Use this sequence after the PR is created and before any broader public
outreach:

1. Record the PR URL and PR head SHA before updating any public proof file.
2. Wait for GitHub Actions `Evidence Court Smoke` to finish on the PR head
   commit.
3. Check the remote `evidence-court-smoke` artifact and confirm the files named
   in the remote evidence checklist above.
4. Update `docs/CURRENT_PROOF_STATUS.md` only after the remote evidence URL,
   run id, commit SHA, and artifact check are known.
5. Do not mark outreach as `sent`, `replied`, or `shared` without a public
   evidence URL for that status.
6. Do not ask trend-watch targets for promotion before PR-head CI evidence
   exists or a first-batch reviewer replies.
7. Do not state external review, endorsement, adoption, share, 10k stars, or
   10000 stars without evidence URLs.

## Safe Boundaries

Say:

- "Evidence Court audits supplied structured JSON run records, explicit marked
  transcript v0 files, and explicit Evidence Court JSONL event streams."
- "Marked transcript v0 is an explicit marker format."
- "The smoke gate is wired into GitHub Actions."
- "Remote CI evidence requires GitHub Actions `Evidence Court Smoke` green for the PR head commit."

Do not say:

- "Native Claude/Codex/Cursor/Devin ingestion is supported."
- "CI logs / GitHub Actions logs are ingested."
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
