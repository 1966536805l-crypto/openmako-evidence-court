# Current Proof Status

This page separates current-main proof evidence from historical release proof.
It is not an automatically updated status page.

## Current Main Proof Anchor

- Branch: `main`
- Current main proof anchor commit: `5836afa6d844348d22433229f2c295023d35d178`
- Current main proof anchor subject: `outreach: render current main review packet`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.

## Local Evidence

These checks passed locally for current main proof anchor commit `5836afa`:

```bash
python3 -m pytest tests/test_evidence_court.py tests/test_evidence_court_smoke_script.py -q
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/openmako-evidence-court-smoke-current-main
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/openmako-evidence-court-smoke-current-main
EVIDENCE_COURT_RUN_URL=https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26958891388 \
  bash scripts/evidence_court_release_set.sh --render-current-main-review-packet
```

Observed local results:

- full local test suite reported `101 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`
- `artifact-manifest.json` SHA-256:
  `2892cfb90026e4585ce2b96392f88daca7969d6f97ac3933ccc3eb72f28d84c3`
- `reviewer-quickstart.md` SHA-256:
  `9a85ed8097563a8dbf6be774bc64080ec2c23bd21dc1721cd4188205a75edc59`

## Public Remote Evidence

Remote CI evidence is confirmed for current main proof anchor commit `5836afa`.

Known facts:

- The commit page for `5836afa` is publicly visible.
- The public Actions run `26958891388` was triggered by push on `main`.
- The public Actions run shows commit `5836afa`.
- The public Actions run shows Status `Success`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest:
  `sha256:e039d6c99b3cf02309fe4633e902f2e0d3a59a4faf40f404b4309c49dddba6e0`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26958891388`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove the latest main commit after `5836afa`.

This page's current main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
