# OpenMako Evidence Court v0.1.1

This patch release keeps the same Evidence Court v0.1 capability boundary and
adds public review assets for safer sharing.

## Added

- `docs/EXPERT_REVIEW_BRIEF.md`: a 30-second review path and safe quote for
  expert reviewers before they share the project.
- `docs/LAUNCH_POST.md`: copyable launch text with the native-ingestion
  boundary.
- `docs/social-card.svg`: a bounded social card that shows the bad-run verdict.

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
- The broader OpenMako coding agent runtime.
- Desktop, quant trading, planner, or autonomous repair capability.

## Verification

```bash
python3 -m pip install .
mako evidence-court --demo bad-run
mako evidence-court --demo good-run --json
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
```
