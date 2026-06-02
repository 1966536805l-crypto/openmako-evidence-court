# Public Proof Card

This page is the shareable proof card for OpenMako Evidence Court v0.1.2. It
binds the public claim to a tag, commit, smoke run, and artifact digest.

## Safe Public Claim

OpenMako Evidence Court v0.1.2 is a small claim-vs-evidence gate for supplied
coding-agent run records. The 10-second demo catches a bad supplied record where
the agent claims tests passed, while the record shows a protected test edit and
no reported required pytest command.

## Evidence Anchor

| Item | Evidence |
| --- | --- |
| Repository | `https://github.com/1966536805l-crypto/openmako-evidence-court` |
| Release tag | `v0.1.2` |
| Tag target commit | `e00cf35a92c09f81ab5cff4169d0dc55fd071811` |
| Release page | `https://github.com/1966536805l-crypto/openmako-evidence-court/releases/tag/v0.1.2` |
| Smoke run | `https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26831075226` |
| Smoke result | GitHub page shows `completed successfully` for commit `e00cf35` |
| Artifact name | `evidence-court-smoke` |
| Artifact digest | `sha256:0f1df42566dbc2352733e3b219117471e0299de3d8004635e265ccd4e9543205` |

## Artifact Review Path

When the remote `evidence-court-smoke` artifact is available, review these files:

| Artifact file | Expected check |
| --- | --- |
| `artifact-manifest.json` | Lists artifact file SHA-256 hashes. |
| `reviewer-quickstart.md` | Gives the 30-second review path and boundary. |
| `bad-run.md` | Shows the bad supplied record verdict as `FAIL`. |
| `good-run.json` | Shows the good supplied record verdict as `PASS`. |
| `marked-transcript.json` | Shows the explicit marked transcript verdict as `FAIL`. |
| `mixed-source-rejection.txt` | Shows mixed evidence sources are rejected with `exit_code=2`. |
| `smoke-summary.txt` | Summarizes the smoke gate output and boundaries. |

## 30-Second Verification

```bash
git clone https://github.com/1966536805l-crypto/openmako-evidence-court.git
cd openmako-evidence-court
git checkout v0.1.2
python3 -m pip install .
mako evidence-court --demo bad-run
```

Expected visible result:

```text
Verdict: FAIL
```

For local artifact verification:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke
```

## What This Proves

- The tagged v0.1.2 code contains the JSON run-record demo.
- The bad supplied record is reported as `FAIL`.
- The smoke workflow completed successfully for the tagged commit.
- The workflow exposed an `evidence-court-smoke` artifact with the digest above.
  The public page proves artifact metadata; download the artifact before
  claiming its contents were independently reverified.
- The public release set includes explicit boundaries for native-ingestion
  claims.

## What This Does Not Prove

- Native Claude/Codex/Cursor/Devin/CI log ingestion.
- That tests actually ran outside the supplied record.
- Broad SWE repair ability.
- The broader OpenMako agent runtime, planner, desktop automation, or quant
  trading capability.
- 10k stars, adoption, or endorsement by any external reviewer.

## Safe Quote

```text
Evidence Court asks a narrow question: does the supplied agent-run record
support the agent's final success claim?
```
