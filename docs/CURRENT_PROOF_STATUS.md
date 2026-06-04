# Current Proof Status

This page separates current-main proof evidence from historical release proof.
It is not an automatically updated status page.

## Current Main Proof Anchor

- Branch: `main`
- Current main proof anchor commit: `6b3f44e2ab2ccbfea97d866b40e0c847395a81ca`
- Current main proof anchor subject: `test: stabilize smoke artifact provenance`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.

## Local Evidence

These checks passed locally for current main proof anchor commit `6b3f44e`:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke-stable-final
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke-stable-final
find /tmp/evidence-court-smoke-stable-final -type f -maxdepth 2 -print | sort | xargs shasum -a 256
```

Observed local results:

- focused Evidence Court tests inside the smoke gate reported `62 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`
- `artifact-manifest.json` SHA-256:
  `2892cfb90026e4585ce2b96392f88daca7969d6f97ac3933ccc3eb72f28d84c3`
- `reviewer-quickstart.md` SHA-256:
  `9a85ed8097563a8dbf6be774bc64080ec2c23bd21dc1721cd4188205a75edc59`

## Public Remote Evidence

Remote CI evidence is confirmed for current main proof anchor commit `6b3f44e`.

Known facts:

- The commit page for `6b3f44e` is publicly visible.
- The public Actions run `26957166830` was triggered by push on `main`.
- The public Actions run shows commit `6b3f44e`.
- The public Actions run shows `completed successfully`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest: `sha256:a2f65c9bec8947c249bfdc276818152fd101caf1d8c1500aa277425a9d6bb780`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26957166830`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove the latest main commit after `6b3f44e`.

This page's current main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
