# Outreach Templates

Use these only after the shared commit has a green `Evidence Court Smoke` run.
The goal is to ask for a quick technical review first, not to imply endorsement.

## Link Set

- Repo: `https://github.com/1966536805l-crypto/openmako-evidence-court`
- Public proof: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md`
- Demo visual: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/demo-terminal.svg`
- Technical review request: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/TECHNICAL_REVIEW_REQUEST.md`
- Open public technical review issue: `https://github.com/1966536805l-crypto/openmako-evidence-court/issues/new?template=technical-review-request.md`
- Release: `https://github.com/1966536805l-crypto/openmako-evidence-court/releases/tag/v0.1.2`
- Current proof status: `https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md`
- Open the proof-status page before trusting or repeating remote CI evidence. It lists the current proof-anchor commit, public Evidence Court Smoke run, artifact digest, and stale-proof boundary.

## General AI Tooling Maintainer

```text
I built a small open-source claim-vs-evidence gate for coding-agent run records:

https://github.com/1966536805l-crypto/openmako-evidence-court

The 10-second demo catches a bad supplied record where the agent says tests
passed, but the record shows a protected test edit and no reported required
pytest command.

If you have 30 seconds, the proof card is here:
https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md

Boundary: v0.1 audits supplied JSON/marked transcript v0/explicit JSONL records.
It does not natively ingest Claude/Codex/Cursor/CI logs and does not prove tests
ran outside the supplied record.
```

## Agent Framework Author

```text
I am working on an evidence layer for agent runs rather than another coding
agent:

https://github.com/1966536805l-crypto/openmako-evidence-court

The current v0.1 checks whether a supplied run record supports the final success
claim: required tests reported, protected files untouched, and scope respected.

The visual demo is intentionally narrow:
https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/demo-terminal.svg

I would value a quick review of whether the claim boundary is honest enough for
me to publish publicly.
```

## CI / DevTools Engineer

```text
I released a small audit gate for coding-agent success claims:

https://github.com/1966536805l-crypto/openmako-evidence-court

It can fail a wrapper/CI path with `--fail-on fail` when the supplied run record
does not support the final claim. The bad demo reports FAIL because the required
pytest command is not reported and a protected test file is edited.

Proof card:
https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md

This is not native CI log ingestion yet; it audits explicit supplied records.
```

## Researcher / Evaluator

```text
I made a minimal open-source evaluator for one failure mode in coding agents:
success claims that are not supported by the supplied run record.

Repo:
https://github.com/1966536805l-crypto/openmako-evidence-court

The first demo is deliberately small: a bad run says tests pass, but the record
shows a protected test edit and no reported required pytest command, so the
verdict is FAIL.

I would appreciate a review of the evidence boundary, especially what should be
added before claiming native agent-log support.
```

## Short Public Post

```text
Agents say "done" too easily.

OpenMako Evidence Court asks a narrower question:
does the supplied run record support the final success claim?

10-second demo: claim says tests passed; supplied record shows a protected test
edit and no reported required pytest command. Verdict: FAIL.

Repo:
https://github.com/1966536805l-crypto/openmako-evidence-court

Proof card:
https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md
```

## Do Not Say

- A specific person has endorsed, recommended, adopted, or deployed the project
  unless they have explicitly done so.
- The project has 10k stars or will definitely reach 10k stars.
- Native Claude/Codex/Cursor/Devin/CI log ingestion is supported.
- Real-world test execution is independently proven outside the supplied record.
- The broader OpenMako agent runtime ships in this public repository.
- Desktop, quant trading, planner, or autonomous repair capability has been
  demonstrated by this public repository.
