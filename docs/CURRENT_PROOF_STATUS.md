# Current Proof Status

This page separates the latest verified main proof anchor from historical
release proof.
It is not an automatically updated status page.

## Latest Verified Main Proof Anchor

- Branch: `main`
- Latest verified main proof anchor commit: `467bc9ba96318cbed5bccfa63167b87efb6a7c13`
- Latest verified main proof anchor subject: `packaging: add discovery metadata`
- Remote `main` contained this commit when checked by `git ls-remote origin refs/heads/main`.
- This anchor can trail the newest remote `main` commit. Re-check Actions before
  repeating any claim about the current remote head.

## Local Evidence

These checks passed locally for latest verified main proof anchor commit
`467bc9b`:

```bash
python3 -m pytest tests/test_evidence_court.py tests/test_evidence_court_smoke_script.py -q
bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/openmako-evidence-court-smoke-current-main-467bc9b
bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/openmako-evidence-court-smoke-current-main-467bc9b
EVIDENCE_COURT_RUN_URL=https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26967812515 \
  bash scripts/evidence_court_release_set.sh --render-current-main-review-packet
```

Observed local results:

- smoke script focused test slice reported `62 passed`
- smoke gate reported `Evidence Court smoke gate passed.`
- local artifact verifier reported `Evidence Court artifact dir verified`
- `artifact-manifest.json` SHA-256:
  `a305534a5e876625a9ebb7e5830f7c478dfd6adb773edde318b08e48fcdf13fb`
- `reviewer-quickstart.md` SHA-256:
  `8155645074fb7acd02b927744a47ac5575a15019919ca6febf61a790918f723d`
- `reason-codes.json` SHA-256:
  `60c860540a73294c265c7a115fd67e7992951d5d740c15c9b69ba6b8a43b7d37`
- `reason-codes.md` SHA-256:
  `871fc58419dee79800c516aa7b05ae124bddbe67f1dd63d5739e671cf448721a`

## Public Remote Evidence

Remote CI evidence is confirmed for latest verified main proof anchor commit
`467bc9b`.

Known facts:

- The commit page for `467bc9b` is publicly visible.
- The public Actions run `26967812515` was triggered by push on `main`.
- The public Actions run shows commit `467bc9b`.
- The public Actions run shows Status `Success`.
- The public job `evidence-court-smoke` shows `completed successfully`.
- The public Actions run uploaded one `evidence-court-smoke` artifact.
- Public artifact digest:
  `sha256:b753e0563d63ca5c0f9c1850b67a13ec9fb2f8f53e5591b9260a93d77561332e`.

Remote evidence URL:
`https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26967812515`

## Historical Release Proof Boundary

`docs/PUBLIC_PROOF.md` intentionally binds the older `v0.1.2` tag, commit,
smoke run, and artifact digest. It remains historical release evidence, but it
does not automatically prove current or later main commits.

This page's latest verified main proof anchor does not automatically prove later commits on `main`.
After any new commit, use the newest visible `Evidence Court Smoke` run and
artifact digest before claiming current remote CI evidence.

## Not Proven

- native Claude/Codex/Cursor/Devin/CI log ingestion
- tests actually ran outside the supplied record
- broad SWE repair ability
- third-party adoption, endorsement, or review
- 10k stars
