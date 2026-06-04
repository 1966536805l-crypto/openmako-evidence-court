# Current Proof Status

This page separates the latest verified main proof anchor from historical
release proof.
It is not an automatically updated status page.

## Latest Verified Main Proof Anchor

- Branch: `main`
- Latest verified main proof anchor commit: `738438b915563c3ad1241a0909ac947697cfd924`
- Latest verified main proof anchor subject: `docs: expose terminal gateway examples`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.
- This anchor can trail the newest remote `main` commit. Re-check Actions before
  repeating any claim about the current remote head.

## Local Evidence

These checks passed locally for latest verified main proof anchor commit
`738438b`:

```bash
python3 -m pytest tests/test_evidence_court.py tests/test_evidence_court_smoke_script.py -q
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/openmako-evidence-court-smoke-current-main
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/openmako-evidence-court-smoke-current-main
EVIDENCE_COURT_RUN_URL=https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26960805210 \
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

Remote CI evidence is confirmed for latest verified main proof anchor commit
`738438b`.

Known facts:

- The commit page for `738438b` is publicly visible.
- The public Actions run `26960805210` was triggered by push on `main`.
- The public Actions run shows commit `738438b`.
- The public Actions run shows Status `Success`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest:
  `sha256:b88802f99f0f6cc3c391cbf86f52757388a23d51ba2779608f98b0ed6643c456`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26960805210`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove the latest main commit after `738438b`.

This page's latest verified main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
