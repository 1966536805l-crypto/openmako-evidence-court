---
name: Technical review request
about: Ask for public feedback on the claim-vs-evidence boundary
title: "Technical review request: claim-vs-evidence boundary for coding-agent runs"
---

This is a public request for technical review, not an endorsement request.
It is not evidence that anyone has reviewed, adopted, endorsed, or shared
OpenMako Evidence Court.
Opening this issue only creates a public request URL. It is not `replied` or
`shared` evidence until a third party posts public feedback or a public share.

## What To Review

OpenMako Evidence Court v0.1.2 asks one narrow question:

```text
Does the supplied coding-agent run record support the agent's final success claim?
```

The bad demo fails because the supplied record says tests passed, but it also
shows a protected test edit and no reported required pytest command.

## Review Questions

1. For a coding-agent run that claims "fixed and tests passed", what minimum
   supplied-record fields should be required before that claim is supportable?
2. If a SWE-Bench-style run lacks the exact eval/test command or edits protected
   tests, should Evidence Court report `FAIL`, or should it use a more granular
   `SUSPICIOUS` verdict?
3. Before claiming native Claude/Codex/Cursor/Devin/CI or framework-log
   ingestion, what adapter evidence should be required beyond this supplied
   JSON/marked-transcript/explicit-JSONL v0.1 support?

## Evidence Links

- Repository: https://github.com/1966536805l-crypto/openmako-evidence-court
- Public proof card: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md
- Demo visual: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/demo-terminal.svg
- Current proof status: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md

Open `docs/CURRENT_PROOF_STATUS.md` before trusting or repeating remote CI
evidence. It lists the current proof-anchor commit, public Evidence Court Smoke
run, artifact digest, and stale-proof boundary.

## Quick Local Check

```bash
git clone https://github.com/1966536805l-crypto/openmako-evidence-court.git
cd openmako-evidence-court
python3 -m pip install .
mako evidence-court --demo bad-run
```

Expected visible result:

```text
Verdict: FAIL
```

## Boundaries

- This does not prove tests actually ran outside the supplied record.
- This does not natively ingest Claude/Codex/Cursor/Devin/CI logs.
- This does not ship the broader OpenMako agent runtime, planner, desktop
  automation, or quant trading capability.
- This does not claim any external reviewer has endorsed, adopted, reviewed, or
  shared the project.
