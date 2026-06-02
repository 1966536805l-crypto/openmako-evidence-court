# OpenMako Evidence Court v0.1.0

Evidence Court audits whether a coding agent's success claim is supported by a
supplied run record.

## Proven In This Release

- Supplied JSON run records can produce `PASS`, `SUSPICIOUS`, or `FAIL`.
- Explicit marked transcript v0 files can be converted into the same run-record
  model.
- Explicit Evidence Court JSONL event streams can be converted into the same
  run-record model.
- `--fail-on fail` returns exit code 1 for a `FAIL` verdict.
- The GitHub Actions smoke gate passed for the release commit.
- The smoke workflow uploads an `evidence-court-smoke` artifact.

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
