# Current Proof Status

This page separates current-main proof evidence from historical release proof.
It is not an automatically updated status page.

## Current Main Proof Anchor

- Branch: `main`
- Current main proof anchor commit: `bec43ca90bdf101bc27cb4f6bdf8e79bf0f4d6c7`
- Current main proof anchor subject: `feat: add protected edit metadata reason codes`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.

## Local Evidence

These checks passed locally for current main proof anchor commit `bec43ca`:

```bash
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-current-main-bec43ca
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-current-main-bec43ca
find /tmp/evidence-court-current-main-bec43ca -type f -maxdepth 2 -print | sort | xargs shasum -a 256
```

Observed local results:

- focused Evidence Court tests inside the smoke gate reported `62 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`
- `artifact-manifest.json` SHA-256:
  `93cc8a7edd8255ab7c58dac8d31cd71bb42d06c15d46d7c3ac5958445d4cd0bb`
- `reviewer-quickstart.md` SHA-256:
  `ef8d78e1c1dde2db8c49efceb96d5fb4c7aeef9d97ef13e7187b574aa8ea3bea`

## Public Remote Evidence

Remote CI evidence is confirmed for current main proof anchor commit `bec43ca`.

Known facts:

- The commit page for `bec43ca` is publicly visible.
- The public Actions run `26954112264` was triggered by push on `main`.
- The public Actions run shows commit `bec43ca`.
- The public Actions run shows `completed successfully`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest: `sha256:e14168486f74639e0dcb296fab3fa313f7b242f653ebffc4f140e2159afa146f`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26954112264`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove the latest main commit after `bec43ca`.

This page's current main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
