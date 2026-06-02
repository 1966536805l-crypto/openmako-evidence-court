# OpenMako Evidence Court v0.1.2

This patch release keeps the Evidence Court v0.1 capability boundary and
packages the public proof and demo assets into an immutable release.

## Added Since v0.1.1

- `docs/PUBLIC_PROOF.md`: a public proof card linking the claim to tag, commit,
  smoke run, artifact metadata, and a 30-second review path.
- `docs/demo-terminal.svg`: a README-safe terminal visual of the supplied
  bad-run demo.
- `docs/OUTREACH.md`: review-first outreach templates for AI tooling, agent
  framework, CI/devtools, and evaluator audiences.
- `docs/OUTREACH_TARGETS.md`: candidate outreach tracker; it is not evidence of
  endorsement, adoption, review, or sharing.

## Proven Scope

- Supplied JSON run records can produce `PASS`, `SUSPICIOUS`, or `FAIL`.
- Explicit marked transcript v0 files can be converted into the same run-record
  model.
- Explicit Evidence Court JSONL event streams can be converted into the same
  run-record model.
- `--fail-on fail` returns exit code 1 for a `FAIL` verdict.
- The smoke gate verifies the public claim boundary.

## Not Claimed

- Native Claude/Codex/Cursor/Devin/CI log ingestion.
- Proof that tests actually ran outside the supplied record.
- Endorsement by any external reviewer.
- The broader OpenMako coding agent runtime.
- Desktop, quant trading, planner, or autonomous repair capability.

## Verification

```bash
git checkout v0.1.2
python3 -m pip install .
mako evidence-court --demo bad-run
mako evidence-court --demo good-run --json
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
```
