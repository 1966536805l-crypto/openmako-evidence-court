# Current Proof Status

This page separates current-main proof evidence from historical release proof.
It is not an automatically updated status page.

## Current Main Proof Anchor

- Branch: `main`
- Current main proof anchor commit: `85223927df6cd010e97adf79c86e130ed1a31193`
- Current main proof anchor subject: `docs: make target packet proof-status based`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.

## Local Evidence

These checks passed locally for current main proof anchor commit `8522392`:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-current-main-8522392
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-current-main-8522392
find /tmp/evidence-court-current-main-8522392 -type f -maxdepth 2 -print | sort | xargs shasum -a 256
```

Observed local results:

- focused Evidence Court tests inside the smoke gate reported `62 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`
- `artifact-manifest.json` SHA-256:
  `78d33ae72348c2b9692ac9b287b228331b1fc597c45d4a7956d5e3d42eacfe2a`
- `reviewer-quickstart.md` SHA-256:
  `ef8d78e1c1dde2db8c49efceb96d5fb4c7aeef9d97ef13e7187b574aa8ea3bea`

## Public Remote Evidence

Remote CI evidence is confirmed for current main proof anchor commit `8522392`.

Known facts:

- The commit page for `8522392` is publicly visible.
- The public Actions run `26955358315` was triggered by push on `main`.
- The public Actions run shows commit `8522392`.
- The public Actions run shows `completed successfully`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest: `sha256:cba645e3fcc7f360b43d997340fcce1563d13b4c9211d527d57d45adee435d60`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26955358315`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove the latest main commit after `8522392`.

This page's current main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
