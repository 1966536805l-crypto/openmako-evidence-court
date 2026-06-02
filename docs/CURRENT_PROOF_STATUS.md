# Current Proof Status

This page separates pinned proof-anchor evidence from latest-main claims.
It is not an automatically updated status page.

## Proof Anchor

- Branch: `main`
- Proof anchor commit: `cb1ab5e`
- Proof anchor subject: `docs: add redacted evidence court bad run`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`

## Local Evidence

These checks passed locally for proof anchor commit `cb1ab5e`:

```bash
python3 -m quantagent.cli --no-trust-prompt evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json
git diff --check
bash scripts/evidence_court_release_set.sh --check
python3 -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q
bash scripts/evidence_court_smoke.sh
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke-redacted
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke-redacted
```

Observed local results:

- redacted supplied-record bad run reports `Verdict: FAIL`
- full focused Evidence Court tests reported `70 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`

## Public Remote Evidence

Remote CI evidence is confirmed for proof anchor commit `cb1ab5e`.

Known facts:

- The commit page for `cb1ab5e` is publicly visible.
- The public Actions run `26836126047` was triggered by push on `main`.
- The public Actions run shows commit `cb1ab5e`.
- The public Actions run shows `Status Success`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Artifact digest: `sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac`.
- The unauthenticated GitHub REST API was rate-limited during earlier verification, so this status is based on the public Actions HTML page and local gates.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26836126047`

## Stale Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It is still useful as historical release
evidence, but it does not prove the latest main commit or the redacted bad-run
fixture.

This page's proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
