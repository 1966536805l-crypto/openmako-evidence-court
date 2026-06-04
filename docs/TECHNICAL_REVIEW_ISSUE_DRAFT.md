# Technical Review Issue Draft

This is a copyable draft for a future public GitHub issue. Do not treat this draft as a sent review request, endorsement, or third-party evidence.

## Title

Technical review request: does Evidence Court keep its claim/evidence boundary tight?

## Body

```markdown
This is a public request for technical review, not an endorsement request.

I am building OpenMako Evidence Court, a small claim-vs-evidence gate for
supplied coding-agent run records. It is not another coding agent.

The narrow question:

> Given a supplied run record, does the final success claim have enough evidence
> inside that record?

### 30-Second Review Path

1. Open `README.md` and run:
   `mako evidence-court --demo bad-run`
2. Open `examples/evidence-court/redacted-real-world-bad-run.json` and run:
   `mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json`
3. Open `docs/EVIDENCE_COURT_COMPARISON.md` for the normal-tests-vs-claim-audit boundary.
4. Open `docs/REDACTION_GUIDE.md` and check whether the redacted fixture is shareable without implying real production proof.
5. Open `docs/CURRENT_PROOF_STATUS.md` before trusting remote CI claims.
6. If checking the current `evidence-court-smoke` artifact, open
   `reason-codes.json` or `reason-codes.md` and confirm `test.required_not_run`
   is listed before judging the CI wrapper recipe.

Expected local behavior:

- the built-in bad demo returns `Verdict: FAIL`
- the redacted supplied-record bad run returns `Verdict: FAIL`
- the redacted bad run flags protected edits and a missing required API guard pytest
- `bash scripts/evidence_court_smoke.sh` passes locally

Current proof status:

- Open before trusting remote CI evidence: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
- The proof-status page lists the current proof-anchor commit, public Evidence Court Smoke run, artifact digest, reason-code artifact files, and stale-proof boundary.
- Do not copy a run URL or digest from this draft without re-opening that page.

### Review Questions

1. Is the README clear that Evidence Court audits only supplied records?
2. Does the redacted fixture improve trust, or does it still look toy-shaped?
3. Are the no-native-ingestion and no-proof-of-real-test-execution boundaries clear enough?
4. Would you accept `--fail-on-reason-code test.required_not_run` as a CI wrapper signal for this narrow audit?
5. What is the most important missing input format or artifact before sharing this more broadly?

### Current Boundary

Evidence Court currently supports supplied JSON run records, explicit marked
transcript v0 files, and explicit Evidence Court JSONL event streams.

It does not claim native Claude/Codex/Cursor/Devin/CI log ingestion.
It does not prove tests actually ran outside the supplied record.
It does not prove broad SWE repair ability.
It does not have third-party endorsement from this issue being opened.

### Links

- README: https://github.com/1966536805l-crypto/openmako-evidence-court
- Normal-tests comparison: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/EVIDENCE_COURT_COMPARISON.md
- Redaction guide: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/REDACTION_GUIDE.md
- Current proof status: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
```

## Do Not Add Before Posting

- “endorsed by”
- “reviewed by”
- “used by”
- “proves tests actually ran”
- “native Claude/Codex/Cursor ingestion”
- “real-world repair accuracy”
- “10k stars”
