# Launch Post

Use this only after the linked GitHub Actions run is green for the commit being
shared.

## Short Version

```text
I released OpenMako Evidence Court v0.1.2.

It is a small claim-vs-evidence gate for coding-agent runs.

The 10-second demo catches a bad run where the agent says tests passed, but the
supplied record shows a protected test edit and no reported required pytest
command.

Verified scope:
- supplied JSON run records
- explicit marked transcript v0 files
- explicit Evidence Court JSONL event streams
- GitHub Actions smoke gate is green
- the workflow uploads an evidence-court-smoke artifact
- the workflow artifact includes reason-codes.json and reason-codes.md for the
  exact CI gate code

Boundary: this does not ingest native Claude/Codex/Cursor/Devin/CI logs, and it
does not prove tests ran outside the supplied record.

Shareable one-liner:
Evidence Court checks whether a coding agent's supplied run record supports its "tests passed" claim.

Repo: https://github.com/1966536805l-crypto/openmako-evidence-court
Release: https://github.com/1966536805l-crypto/openmako-evidence-court/releases/tag/v0.1.2
Current proof status: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
```

## Review Path

1. Open the repository.
2. Check the green `Evidence Court Smoke` workflow.
3. Open the `v0.1.2` tag.
4. Open `docs/CURRENT_PROOF_STATUS.md` before trusting remote CI evidence.
5. Open the current `evidence-court-smoke` artifact and check
   `reason-codes.json` or `reason-codes.md` for `test.required_not_run`.
6. Run `mako evidence-court --demo bad-run`.
7. Read `docs/EXPERT_REVIEW_BRIEF.md`.

## Do Not Say

- Native Claude/Codex/Cursor/Devin/CI log ingestion is supported.
- Evidence Court proves tests actually ran outside the supplied record.
- The broader OpenMako coding agent runtime ships in this public repo.
- Desktop, quant trading, planner, or autonomous repair capability is proven.
