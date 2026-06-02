# Technical Review Request

This is a 30-second public request for technical review by coding-agent
builders: does an agent success claim have enough evidence?
This is not an endorsement request and is not asking for endorsement or a share.
It is not evidence that anyone has reviewed, adopted, or shared OpenMako
Evidence Court.

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

- Repository: `https://github.com/1966536805l-crypto/openmako-evidence-court`
- Public proof card: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md`
- Demo visual: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/demo-terminal.svg`
- Reference green smoke run: `https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26836126047`
- Reference smoke artifact digest: `sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac`

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

## How To Respond

Public technical feedback is most useful because it can be linked from
`docs/OUTREACH_TARGETS.md`. If feedback happens in a private channel, do not
record it as public `sent`, `replied`, or `shared` evidence unless there is a
public URL. Repository docs, release pages, and launch posts are not valid
`Message URL`, `Reply URL`, or `Share URL` evidence for a third-party target.
