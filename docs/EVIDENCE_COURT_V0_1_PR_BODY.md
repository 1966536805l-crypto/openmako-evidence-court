# Evidence Court v0.1 PR Body

Copy this into the GitHub PR body for the Evidence Court v0.1 release
candidate.

````markdown
## Evidence Court v0.1

### Claim
OpenMako Evidence Court audits supplied structured JSON run records, explicit
marked transcript v0 files, explicit Evidence Court JSONL event streams, and
supplied pytest logs, GitHub Actions test-step logs, or GitHub Actions job logs
with visible supported test commands. It checks whether the final success claim
is supported inside the supplied record or supplied log by reported files,
reported commands, reported test output, and scope boundaries.

This PR does not claim native Claude/Codex/Cursor/Devin transcript ingestion,
arbitrary CI log ingestion, real-world proof that tests ran outside the supplied
record/log, broad SWE-style repair, unknown NPM reasoning, or Desktop L4/L5
autonomy.

Packaging boundary: The open-mako wheel for this release installs only the
narrow quantagent package surface required by Evidence Court:
`quantagent.__init__` and `quantagent.evidence_court`. Broader OpenMako and
quantagent runtime modules are outside this launch claim unless covered by
separate gates.

### User-Facing Demo
```bash
mako evidence-court --demo bad-run
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
```

Expected demo behavior:
- bad demo reports `Verdict: FAIL`
- good demo JSON reports `"verdict": "PASS"`
- marked transcript v0 fixture reports `"verdict": "FAIL"`
- supplied GitHub Actions pytest test-step log reports `"verdict": "PASS"`
- supplied GitHub Actions job log reports `"verdict": "PASS"`
- supplied failed pytest log reports `"verdict": "FAIL"`
- mixed JSON plus transcript inputs are rejected

### 30-Second Reviewer Path
Open these first:
1. `bad-run.md`: the supplied record claims success but shows a protected test edit and missing reported required pytest.
2. `fail-on-fail.json`: the same bad run under `--fail-on fail` exits 1 for CI/wrappers.
3. `artifact-manifest.json`: safe claim, expected artifact checks, source provenance checks, artifact file SHA-256 hashes, and boundaries.
4. `reviewer-quickstart.md`: copy-paste local/remote review path and source provenance checks.
5. `jsonl-events.json`: explicit Evidence Court JSONL event-stream input.
6. `github-actions-test-step.json`: supplied GitHub Actions pytest test-step log returns `"verdict": "PASS"`.
7. `github-actions-job-log.json`: supplied GitHub Actions job log returns `"verdict": "PASS"`.
8. `failed-pytest-log.json`: supplied failed pytest log returns `"verdict": "FAIL"`.
9. `mixed-source-rejection.txt`: mixed inputs fail closed with `exit_code=2`.

### Included In This Release Claim
- `.github/workflows/evidence-court.yml`
- `LICENSE`
- `README.md`
- `docs/CAPABILITY_GATES.md`
- `docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`
- `docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md`
- `docs/EVIDENCE_COURT_V0_1_PR_BODY.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md`
- `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`
- `examples/evidence-court/bad-run.json`
- `examples/evidence-court/good-run.json`
- `MANIFEST.in`
- `pyproject.toml`
- `quantagent/__init__.py`
- `quantagent/evidence_court.py`
- `scripts/evidence_court_release_set.sh`
- `scripts/evidence_court_smoke.sh`
- `setup.py`
- `tests/fixtures/evidence_court/marked_bad_transcript.txt`
- `tests/test_evidence_court.py`
- `tests/test_evidence_court_smoke_script.py`

### Excluded From This Claim
- `quantagent/agent_planner.py`
- `quantagent/cli.py`
- `tests/test_agent_planner_contract.py`
- `tests/test_external_benchmark_multimodule_regression.py`

These files may exist in the branch, but they do not support the Evidence Court
v0.1 public claim.

### Local Evidence
- [ ] `bash scripts/evidence_court_smoke.sh`
- [ ] `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`
- [ ] `bash scripts/evidence_court_release_set.sh --check`
- [ ] `bash scripts/evidence_court_release_set.sh --check-staged-release-set`
- [ ] `bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy`
- [ ] `bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke`
- [ ] `python3 -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q`
- [ ] `git diff --check`
- [ ] After the release commit: `bash scripts/evidence_court_release_set.sh --check-branch-diff origin/main`

### Local Artifact Review Path
Before remote CI exists:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
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
      `good-run.json` shows `"verdict": "PASS"`; `marked-transcript.json`
      shows `"verdict": "FAIL"`; `jsonl-events.json` shows
      `"verdict": "FAIL"`; `openmako-agent-result.json` shows
      `"verdict": "FAIL"`; `github-actions-test-step.json` shows
      `"verdict": "PASS"`; `github-actions-job-log.json` shows
      `"verdict": "PASS"`; `failed-pytest-log.json` shows
      `"verdict": "FAIL"`; `mixed-source-rejection.txt` shows `exit_code=2`;
      report artifacts include `source: ...`; `artifact-manifest.json`
      includes SHA-256 hashes for every file in the review path;
      `smoke-summary.txt` shows `Evidence Court smoke gate passed.`
- [ ] `bash scripts/evidence_court_release_set.sh --verify-artifact-dir <artifact-dir>`
      passes on the downloaded artifact directory.

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

### Launch Copy
I built OpenMako Evidence Court, a claim-vs-evidence gate for supplied agent-run records.

Agents often say "done" or "tests passed". Evidence Court checks the supplied
run record: what files were reported as read, what files were reported as
changed, what commands were reported, what test output was supplied, and whether
the edit stayed in scope.

Retweet-sized version:
Agents often say "done" or "tests passed". OpenMako Evidence Court audits the
supplied run record and flags missing reported required tests,
protected-file edits, out-of-scope changes, and unsupported success claims.

Try:
  mako evidence-court --demo bad-run
  bash scripts/evidence_court_smoke.sh
  bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
````
