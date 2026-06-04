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

30-second share block:
OpenMako Evidence Court is a small CI-friendly record auditor for coding-agent "tests passed" claims.
Try: mako evidence-court --input examples/evidence-court/bad-run.json --fail-on-reason-code test.required_not_run --json
Boundary: audits supplied records only; not native Claude/Codex/Cursor/CI log ingestion and not proof tests ran outside the record.

Repo: https://github.com/1966536805l-crypto/openmako-evidence-court
Release: https://github.com/1966536805l-crypto/openmako-evidence-court/releases/tag/v0.1.2
Current proof status: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
```

## Share Kit

Use this section when someone is deciding whether to share OpenMako Evidence
Court. It is designed for accurate third-party posts, not endorsement claims.

Before sharing, check that the current `Evidence Court Smoke` badge is green and
open `docs/CURRENT_PROOF_STATUS.md`. Do not repeat a run URL, artifact digest,
or current-main claim unless that proof-status page or the run page supports it.

### Safe Short Post

```text
Coding agents often say "done" or "tests passed" before the supplied run record supports it.

OpenMako Evidence Court is a small CI-friendly record auditor for that gap.

The demo fails a bad record that claims tests passed while omitting the required pytest command and editing a protected test file.

Repo:
https://github.com/1966536805l-crypto/openmako-evidence-court

Proof status:
https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
```

### Technical Share

```text
The useful boundary in OpenMako Evidence Court is not "agent quality"; it is claim-vs-evidence.

Example CI gate:
mako evidence-court --input examples/evidence-court/bad-run.json --fail-on-reason-code test.required_not_run --json

That exact gate exits 1 when the supplied record omits the required test command.

Boundary: it audits supplied records only. It does not natively ingest Claude/Codex/Cursor/CI logs and does not prove tests ran outside the record.
```

### Share Only If

- The post says Evidence Court audits supplied records.
- The post keeps `test.required_not_run` as a narrow CI reason-code example.
- The post links to current proof status before citing remote CI evidence.
- Any external review, endorsement, adoption, or share claim has a public
  evidence URL.
- The post does not imply external endorsement, adoption, review, or a share.

### Star Request Boundary

It is acceptable to ask people to star the repository if they want a small,
bounded CI gate for unsupported coding-agent success claims. Do not ask for
stars by implying endorsement, adoption, proven usefulness, or milestone
progress that does not exist.

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
