# Outreach Targets

This tracker turns `docs/OUTREACH.md` into an execution plan. Every entry below
is a candidate for review-first outreach. None of these people, projects, or organizations has endorsed, reviewed, adopted, or shared OpenMako Evidence Court.
This file is not evidence of interest, adoption, endorsement, review, or sharing.

## Rules

- Ask for a 30-second technical review before asking for a share.
- Use the `v0.1.2` release, `docs/PUBLIC_PROOF.md`, and `docs/demo-terminal.svg`
  as the evidence bundle.
- Do not imply endorsement, partnership, usage, or affiliation.
- Do not open issues unless the target project welcomes ecosystem/tooling
  discussion there; prefer discussions, forums, public community channels, or a
  personal channel the target already publishes.
- One polite message per target. No follow-up unless they reply.

## Status Key

| Status | Meaning |
| --- | --- |
| `candidate` | Good fit, not contacted. |
| `drafted` | Message drafted, not sent. |
| `sent` | Message sent. |
| `replied` | Target replied. |
| `shared` | Target publicly shared; requires a public share URL in the tracking table. |
| `closed` | No further action. |

## Target List

| Priority | Target | Bucket | Public source | Why it fits | Suggested channel | Template | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | OpenHands | coding-agent scaffold | `https://github.com/OpenHands/OpenHands` | Coding-agent builders care about run evidence, sandboxing, and SWE-Bench-style claims. | GitHub Discussions or community channel | Agent Framework Author | candidate |
| 2 | SWE-agent / mini-SWE-agent | coding-agent scaffold | `https://github.com/SWE-agent/mini-swe-agent` | SWE-Bench-oriented agent maintainers are a direct fit for claim-vs-evidence checks. | GitHub issue question template | Researcher / Evaluator | sent |
| 3 | Aider | coding assistant | `https://github.com/Aider-AI/aider` | Terminal coding-agent users understand test-claim gaps and CLI gates. | GitHub Discussions/community channel | CI / DevTools Engineer | candidate |
| 4 | Cline | coding agent | `https://github.com/cline/cline` | Open-source IDE/CLI agent with human-in-the-loop workflows that could benefit from supplied-record audit language. | Public community channel, not unsolicited issue spam | Agent Framework Author | candidate |
| 5 | Continue | coding assistant | `https://github.com/continuedev/continue` | IDE and CLI assistant ecosystem; useful target for honest run-record boundary feedback. | Community forum or public discussion | General AI Tooling Maintainer | candidate |
| 6 | LangGraph | agent framework | `https://github.com/langchain-ai/langgraph` | Agent orchestration maintainers care about state, observability, and eval traces. | LangChain forum or GitHub Discussions | General AI Tooling Maintainer | candidate |
| 7 | LangChain Open SWE | coding agent | `https://github.com/langchain-ai/open-swe` | Open-source asynchronous coding-agent project; direct evidence-gate fit. | GitHub Discussions General category | Agent Framework Author | drafted |
| 8 | LangChain Deep Agents | agent harness | `https://github.com/langchain-ai/deepagents` | Harness-level agent builders can review whether Evidence Court fits agent artifacts. | LangChain forum | Agent Framework Author | candidate |
| 9 | Microsoft AutoGen | multi-agent framework | `https://github.com/microsoft/autogen` | Multi-agent framework with benchmark/devtool history; useful boundary reviewer despite maintenance mode. | GitHub Discussions if active, otherwise no issue | General AI Tooling Maintainer | candidate |
| 10 | CrewAI | multi-agent framework | `https://github.com/crewAIInc/crewAI` | Large multi-agent community; supplied-run evidence could fit crew execution reporting. | Community forum/GitHub discussion | Agent Framework Author | candidate |
| 11 | Mastra | TypeScript agent framework | `https://github.com/mastra-ai/mastra` | TypeScript agent framework with eval/observability interests. | GitHub Discussions/community channel | General AI Tooling Maintainer | candidate |
| 12 | Google ADK Python | agent development kit | `https://github.com/google/adk-python` | Agent SDK/toolkit maintainers can judge whether the proof boundary is useful for agent runs. | GitHub Discussions or public community channel | General AI Tooling Maintainer | candidate |
| 13 | OpenAI Agents SDK docs | agent SDK | `https://developers.openai.com/api/docs/guides/agents` | SDK users need artifact/run-record patterns; do not imply OpenAI endorsement. | Public forum or personal channel only | General AI Tooling Maintainer | candidate |
| 14 | Pydantic AI | agent framework | `https://github.com/pydantic/pydantic-ai` | Typed agent framework; useful reviewer for schema and structured run-record design. | GitHub Discussions/community channel | General AI Tooling Maintainer | candidate |
| 15 | Agno | agent platform SDK | `https://github.com/agno-agi/agno` | Agent platform SDK; good fit for supplied-record proof and guardrail review. | Community channel | General AI Tooling Maintainer | candidate |
| 16 | SWE-bench | coding-agent benchmark | `https://github.com/SWE-bench/SWE-bench` | Benchmark maintainers understand success-claim evidence and test-result boundaries. | GitHub issue question template | Researcher / Evaluator | sent |
| 17 | Terminal-Bench | agent benchmark | `https://www.tbench.ai/` | Terminal-task benchmark community cares about command evidence and artifact verification. | Project/community channel | Researcher / Evaluator | candidate |
| 18 | GitTaskBench | coding-agent benchmark | `https://github.com/QuantaAlpha/GitTaskBench` | Repository-level task benchmark; good fit for claim/evidence/scope checks. | GitHub issue only if feedback/tooling discussion is welcome | Researcher / Evaluator | candidate |
| 19 | SWE-PolyBench | coding-agent benchmark | `https://github.com/amazon-science/SWE-PolyBench` | Multi-language repository benchmark; target for honest evaluation artifact discussion. | GitHub issue only if relevant | Researcher / Evaluator | candidate |
| 20 | SWE-Bench-CL | continual-learning benchmark | `https://github.com/thomasjoshi/agents-never-forget` | Continual coding-agent benchmark; useful reviewer for trajectory and evidence reuse boundaries. | GitHub discussion/issue only if appropriate | Researcher / Evaluator | candidate |
| 21 | Hermes Agent | local agent / gateway | `https://github.com/NousResearch/hermes-agent` | High-visibility local agent/gateway project with Codex, Claude Code, OpenClaw, memory, and subagent themes; useful for checking whether Evidence Court's supplied-record boundary fits fast-moving local-agent workflows. | Public community channel or GitHub Discussions if active; no unsolicited issue spam | Agent Framework Author | candidate |
| 22 | OpenClaw | local agent / gateway | `https://github.com/openclaw/openclaw` | Local-first gateway/sandbox/approval-style agent workflow; useful for feedback on run-record fields around tool calls, permission boundaries, and final success claims. | Public community channel or GitHub Discussions if active; no unsolicited issue spam | Agent Framework Author | candidate |
| 23 | opencode | terminal coding agent | `https://github.com/sst/opencode` | Fast terminal/TUI coding-agent ecosystem; useful target for the new reason-code CI recipe and command-history evidence boundary. | Public community channel or GitHub Discussions if active; no unsolicited issue spam | CI / DevTools Engineer | candidate |

## First Batch

Start with five targets before scaling:

1. SWE-agent / mini-SWE-agent
2. Aider
3. OpenHands
4. SWE-bench
5. LangGraph

Reason: these are closest to coding-agent evidence and benchmark claims. A
future concrete technical review from any one of them would be more valuable
than sending weak messages to all 20.

## Recommended Send Order

| Rank | Target | Reason |
| --- | --- | --- |
| 1 | SWE-agent / mini-SWE-agent | Strongest technical match: SWE-Bench-style trajectories, test/eval command evidence, and benchmark claims are central to their context. |
| 2 | Aider | Strongest user-conversion match: terminal coding-assistant users understand "tests passed" claims, command history, edited files, and test output. |
| 3 | OpenHands | Largest reach, but the community is broader and noisier; send after the wording is tightened by at least one external review or manual pass. |
| 4 | SWE-bench | Highest potential evaluation relevance, but less likely to convert directly into user stars than an agent-tool community. |
| 5 | LangGraph | Large agent ecosystem, but current v0.1 has no LangGraph trace adapter; ask only about future explicit JSONL event mapping. |

## Trend-Watch Targets

Do not send these before current main has public green CI evidence or at least
one first-batch reply. They are high-reach local-agent projects, so weak wording
would look like promotion instead of technical review.

| Target | Trend signal | Specific ask | Boundary to keep |
| --- | --- | --- | --- |
| Hermes Agent | Local agent/gateway, memory, subagents, and cross-provider workflows. | Would a supplied Evidence Court run record be useful as a lightweight post-run audit artifact for local-agent sessions? | Evidence Court does not ingest Hermes/OpenClaw native logs; it only audits explicit supplied records. |
| OpenClaw | Local gateway, sandboxing, approvals, and human-controlled agent execution. | What fields should represent approval/tool-call boundaries before a final "done" claim is supportable? | No affiliation, adoption, integration, or sandbox proof is claimed. |
| opencode | Terminal/TUI coding-agent workflow and command-history evidence. | Is the `--fail-on-reason-code test.required_not_run` CI recipe understandable enough for a terminal-agent user? | It is a CI wrapper recipe for supplied records, not native opencode ingestion. |

## First-Batch Contact URLs

| Target | Contact URL | Public source checked | Channel rule |
| --- | --- | --- | --- |
| OpenHands | `https://dub.sh/openhands` | OpenHands README links to Slack and also points feature requests to GitHub issues. | Ask in community Slack first; do not open an issue unless maintainers direct it there. |
| SWE-agent / mini-SWE-agent | `https://join.slack.com/t/swe-bench/shared_invite/zt-36pj9bu5s-o3_yXPZbaH2wVnxnss1EkQ` | mini-SWE-agent README exposes a SWE-bench Slack badge. | Ask in Slack as a benchmark/evidence-boundary review, not as an integration request. |
| Aider | `https://discord.gg/Y7X7bhMQFV` | Aider README lists a Discord Community. | Ask in Discord only if there is a relevant community channel; do not file a repo issue. |
| LangGraph | `https://forum.langchain.com` | LangGraph README sends technical questions, ideas, and feedback to the LangChain Forum. | Use the forum; frame as trace-to-supplied-record schema feedback. |
| SWE-bench | `https://github.com/SWE-bench/SWE-bench/issues/new/choose` | SWE-bench README welcomes contributions, pull requests, or issues. | Open only if the issue template fits evidence-boundary feedback; otherwise use the listed academic contacts manually. |

## First-Batch Specific Asks

| Target | Specific review ask | Why this target | Evidence boundary to mention |
| --- | --- | --- | --- |
| OpenHands | What fields should a supplied coding-agent run record contain before a claim like "fixed and tests passed" is considered supported? | OpenHands exposes SDK, CLI, local GUI, and evaluation infrastructure, so run-record boundaries are directly relevant. | Evidence Court audits supplied records only; it does not prove real test execution outside the record. |
| SWE-agent / mini-SWE-agent | If a SWE-Bench-style run lacks the exact eval/test command or edits a protected test file, should the verdict be `FAIL` or a more granular `SUSPICIOUS`? | mini-SWE-agent emphasizes a minimal linear trajectory and SWE-bench verified performance, so claim/eval evidence wording matters. | Evidence Court is not scoring SWE-Bench performance; it checks whether the supplied evidence supports the final claim. |
| Aider | For terminal pair-programming, is command history plus edited files plus test output enough, or should a supplied record also include diff/protected-path data? | Aider highlights linting and testing after edits, making test-claim gaps easy for its users to evaluate. | Evidence Court only checks reported commands/output; it does not natively ingest Aider logs. |
| LangGraph | Which trace fields would be necessary to convert a LangGraph run into explicit Evidence Court JSONL events without claiming native ingestion? | LangGraph and LangSmith focus on stateful agents, trajectories, tracing, and observability. | Any LangGraph mapping would be a future adapter; current v0.1 accepts explicit supplied records only. |
| SWE-bench | For benchmark maintainers, what minimum artifact set should be required before an agent's "solved" claim is evidence-supported? | SWE-bench centers reproducible evaluation, Docker logs, predictions, run IDs, and final results. | Evidence Court does not replace benchmark scoring; it audits whether claim, scope, commands, and outputs line up. |

## Immediate Send Packet

Send only the first message first. Send the second message only after recording a
public `Message URL` for the first one, or after one calendar day with no reply.
If the channel does not provide a public URL, do not mark the row as `sent`.

Use the current-main packet below when the target is reviewing current main
behavior rather than the older v0.1.2 proof card. Refresh the commit and CI run
immediately before sending. Do not add an artifact digest unless the public
Actions artifact metadata is visible at send time. Do not mark this packet as
sent until the actual message has a public URL.

Fill `<MAIN_SHA>` from `git ls-remote origin refs/heads/main` and `<RUN_URL>`
from the latest successful public `Evidence Court Smoke` run for that exact
commit.

### Current Main Evidence Packet

```text
I added current-main evidence for the supplied-record boundary:
Repo: https://github.com/1966536805l-crypto/openmako-evidence-court
Main commit: <MAIN_SHA>
CI: <RUN_URL>
Artifact digest: not included here; verify public Actions artifact metadata before claiming artifact contents.

The current run-record schema preserves optional metadata like agent_runtime,
tool_calls, approval_events, sandbox_boundary, diff_summary, artifact_urls, and
redaction_note, but those fields are reviewer context only. They do not prove
sandboxing, approval, native log ingestion, or real test execution.

Could you give one technical boundary check: is this supplied-record handoff
shape useful for coding-agent runs, or is a required field missing?
Not asking for endorsement, adoption, or a share.
```

### 1. SWE-agent / mini-SWE-agent

```text
Hi, I built a tiny v0.1.2 gate for checking whether a coding-agent "fixed/tests passed" claim is backed by its supplied run record: https://github.com/1966536805l-crypto/openmako-evidence-court
From a SWE-Bench / mini-SWE-agent perspective, is this verdict boundary too strict, too weak, or useful?
Review request: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/TECHNICAL_REVIEW_REQUEST.md
Not asking for endorsement or a share; I only want technical boundary feedback.
```

### 2. Aider

```text
Hi, I built a small v0.1.2 audit gate for terminal coding-agent run records: https://github.com/1966536805l-crypto/openmako-evidence-court
For an Aider-style workflow, what should the supplied record include before a "tests passed" claim is supportable?
Review request: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/TECHNICAL_REVIEW_REQUEST.md
Not asking for endorsement or a share; I only want technical boundary feedback.
```

### 3. LangChain Open SWE

Title:

```text
Boundary check: minimum supplied-record fields before "fixed/tests passed" claims
```

Body:

```text
I built a narrow claim-vs-evidence gate for supplied coding-agent run records:
https://github.com/1966536805l-crypto/openmako-evidence-court

Current proof status:
- Proof status: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/CURRENT_PROOF_STATUS.md
- Field checklist: https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/RUN_RECORD_FIELD_CHECKLIST.md

Open the proof-status page before trusting remote CI evidence. It lists the
current proof-anchor commit, public Evidence Court Smoke run, artifact digest,
and stale-proof boundary.

Open SWE is close to the workflow I want feedback from: internal coding agents,
sandboxed execution, PR creation, and human-visible artifacts.

Technical boundary question:
before an agent says "fixed and tests passed", is this minimum supplied-record
shape useful, or is a required field missing?

- final claim
- task boundary
- files read/edited
- commands run
- required test/eval command
- supplied test output
- protected paths
- approval/sandbox/tool-call metadata as context only
- public artifact URLs when available

Boundary: Evidence Court only audits explicit supplied records. It does not
natively ingest Open SWE/LangGraph logs, does not prove real test execution
outside the record, and does not claim adoption, endorsement, integration, or a
share. I am asking for technical boundary criticism only.
```

## First-Batch Send Drafts

### OpenHands

```text
I built a small v0.1.2 claim-vs-evidence gate for supplied coding-agent run
records:
https://github.com/1966536805l-crypto/openmako-evidence-court

Could I get a quick technical review from an OpenHands perspective? For a run
that says "fixed and tests passed", what fields should the supplied record
contain before that claim is supportable?

Proof card: docs/PUBLIC_PROOF.md. Demo: docs/demo-terminal.svg.
Not asking you to endorse or share it; I want boundary feedback first.
```

### SWE-agent / mini-SWE-agent

```text
I made a narrow v0.1.2 evidence gate for coding-agent success claims:
https://github.com/1966536805l-crypto/openmako-evidence-court

Could I get a quick technical review from a SWE-Bench / mini-SWE-agent angle?
If a supplied run lacks the exact eval/test command, or edits a protected test
file, should the verdict be FAIL or a more granular SUSPICIOUS?

Proof card: docs/PUBLIC_PROOF.md. Demo: docs/demo-terminal.svg.
Not asking for endorsement or a share; just boundary feedback.
```

### Aider

```text
I built a small v0.1.2 audit gate for coding-agent run records:
https://github.com/1966536805l-crypto/openmako-evidence-court

Could I get a quick technical review from an Aider/terminal workflow angle? Is
command history plus edited files plus test output enough for a supplied record,
or should diff/protected-path data be required to catch "tests passed" claims?

Proof card: docs/PUBLIC_PROOF.md. Demo: docs/demo-terminal.svg.
Not asking you to endorse or share it; I want the boundary to be honest first.
```

### LangGraph

```text
I made a narrow v0.1.2 claim-vs-evidence gate for supplied agent-run records:
https://github.com/1966536805l-crypto/openmako-evidence-court

Could I get a quick technical review from a LangGraph trace perspective? Which
node/tool-call/state fields would be necessary to convert a trace into explicit
Evidence Court JSONL events without claiming native LangGraph ingestion?

Proof card: docs/PUBLIC_PROOF.md. Demo: docs/demo-terminal.svg.
Not asking for endorsement or a share; just schema-boundary feedback.
```

### SWE-bench

```text
I built a small v0.1.2 evidence gate for coding-agent success claims:
https://github.com/1966536805l-crypto/openmako-evidence-court

Could I get a quick technical review from a benchmark-maintainer angle? Before
an agent claims an issue is solved, what minimum artifact set should support the
claim: issue id, patch files, allowed/protected scope, eval command, eval
output, final claim, or something else?

Proof card: docs/PUBLIC_PROOF.md. Demo: docs/demo-terminal.svg.
Not asking for endorsement or a share; just evidence-boundary feedback.
```

## Tracking Fields To Fill After Sending

Do not change a target from `candidate` or `drafted` to `sent`, `replied`, or
`shared` without public evidence URLs. For private channels with no public
message URL, keep the status as `drafted` and record the private send outside
this public tracker.

| Target | Status | Sent date | Contact URL | Message URL | Reply date | Reply URL | Share URL | Message variant | Action needed | Outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SWE-agent / mini-SWE-agent | sent | 2026-06-03 | `https://github.com/SWE-agent/mini-swe-agent/issues/848` | `https://github.com/SWE-agent/mini-swe-agent/issues/848` |  |  |  | GitHub issue question template | Wait for technical boundary feedback; do not follow up unless they reply. | Public issue opened; no reply yet. |
| Aider | candidate |  | `https://discord.gg/Y7X7bhMQFV` |  |  |  |  | Immediate #2 | Send second only after first message URL is recorded, or after one calendar day. |  |
| OpenHands | candidate |  | `https://dub.sh/openhands` |  |  |  |  | First-Batch Draft | Wait until wording is tightened by a manual pass or external review. |  |
| LangChain Open SWE | drafted |  | `https://github.com/langchain-ai/open-swe/discussions/new?category=general` |  |  |  |  | Immediate #3 | Ready to submit to the General Discussion category after final third-party posting confirmation; do not mark `sent` without the discussion URL. | Draft prepared from current-main CI evidence and run-record field checklist. |
| SWE-bench | sent | 2026-06-03 | `https://github.com/SWE-bench/SWE-bench/issues/595` | `https://github.com/SWE-bench/SWE-bench/issues/595` |  |  |  | GitHub issue question template | Wait for technical boundary feedback; do not follow up unless they reply. | Public issue opened; no reply yet. |
| LangGraph | candidate |  | `https://forum.langchain.com` |  |  |  |  | First-Batch Draft | Wait; current v0.1 has no LangGraph trace adapter. |  |

## Do Not Say

- Any target endorsed, reviewed, adopted, deployed, or shared the project until
  there is public evidence.
- The project has reached major-star milestones.
- Native Claude/Codex/Cursor/Devin/CI log ingestion is supported.
- Evidence Court proves tests actually ran outside the supplied record.
- OpenMako's broader agent runtime ships in this repository.
