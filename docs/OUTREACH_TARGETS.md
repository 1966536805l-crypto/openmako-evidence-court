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
| 2 | SWE-agent / mini-SWE-agent | coding-agent scaffold | `https://github.com/SWE-agent/mini-swe-agent` | SWE-Bench-oriented agent maintainers are a direct fit for claim-vs-evidence checks. | GitHub Discussions or issue only if ecosystem discussion is welcome | Researcher / Evaluator | candidate |
| 3 | Aider | coding assistant | `https://github.com/Aider-AI/aider` | Terminal coding-agent users understand test-claim gaps and CLI gates. | GitHub Discussions/community channel | CI / DevTools Engineer | candidate |
| 4 | Cline | coding agent | `https://github.com/cline/cline` | Open-source IDE/CLI agent with human-in-the-loop workflows that could benefit from supplied-record audit language. | Public community channel, not unsolicited issue spam | Agent Framework Author | candidate |
| 5 | Continue | coding assistant | `https://github.com/continuedev/continue` | IDE and CLI assistant ecosystem; useful target for honest run-record boundary feedback. | Community forum or public discussion | General AI Tooling Maintainer | candidate |
| 6 | LangGraph | agent framework | `https://github.com/langchain-ai/langgraph` | Agent orchestration maintainers care about state, observability, and eval traces. | LangChain forum or GitHub Discussions | General AI Tooling Maintainer | candidate |
| 7 | LangChain Open SWE | coding agent | `https://github.com/langchain-ai/open-swe` | Open-source asynchronous coding-agent project; direct evidence-gate fit. | GitHub Discussions/community channel | Agent Framework Author | candidate |
| 8 | LangChain Deep Agents | agent harness | `https://github.com/langchain-ai/deepagents` | Harness-level agent builders can review whether Evidence Court fits agent artifacts. | LangChain forum | Agent Framework Author | candidate |
| 9 | Microsoft AutoGen | multi-agent framework | `https://github.com/microsoft/autogen` | Multi-agent framework with benchmark/devtool history; useful boundary reviewer despite maintenance mode. | GitHub Discussions if active, otherwise no issue | General AI Tooling Maintainer | candidate |
| 10 | CrewAI | multi-agent framework | `https://github.com/crewAIInc/crewAI` | Large multi-agent community; supplied-run evidence could fit crew execution reporting. | Community forum/GitHub discussion | Agent Framework Author | candidate |
| 11 | Mastra | TypeScript agent framework | `https://github.com/mastra-ai/mastra` | TypeScript agent framework with eval/observability interests. | GitHub Discussions/community channel | General AI Tooling Maintainer | candidate |
| 12 | Google ADK Python | agent development kit | `https://github.com/google/adk-python` | Agent SDK/toolkit maintainers can judge whether the proof boundary is useful for agent runs. | GitHub Discussions or public community channel | General AI Tooling Maintainer | candidate |
| 13 | OpenAI Agents SDK docs | agent SDK | `https://developers.openai.com/api/docs/guides/agents` | SDK users need artifact/run-record patterns; do not imply OpenAI endorsement. | Public forum or personal channel only | General AI Tooling Maintainer | candidate |
| 14 | Pydantic AI | agent framework | `https://github.com/pydantic/pydantic-ai` | Typed agent framework; useful reviewer for schema and structured run-record design. | GitHub Discussions/community channel | General AI Tooling Maintainer | candidate |
| 15 | Agno | agent platform SDK | `https://github.com/agno-agi/agno` | Agent platform SDK; good fit for supplied-record proof and guardrail review. | Community channel | General AI Tooling Maintainer | candidate |
| 16 | SWE-bench | coding-agent benchmark | `https://github.com/SWE-bench/SWE-bench` | Benchmark maintainers understand success-claim evidence and test-result boundaries. | GitHub Discussions or academic contact channel | Researcher / Evaluator | candidate |
| 17 | Terminal-Bench | agent benchmark | `https://www.tbench.ai/` | Terminal-task benchmark community cares about command evidence and artifact verification. | Project/community channel | Researcher / Evaluator | candidate |
| 18 | GitTaskBench | coding-agent benchmark | `https://github.com/QuantaAlpha/GitTaskBench` | Repository-level task benchmark; good fit for claim/evidence/scope checks. | GitHub issue only if feedback/tooling discussion is welcome | Researcher / Evaluator | candidate |
| 19 | SWE-PolyBench | coding-agent benchmark | `https://github.com/amazon-science/SWE-PolyBench` | Multi-language repository benchmark; target for honest evaluation artifact discussion. | GitHub issue only if relevant | Researcher / Evaluator | candidate |
| 20 | SWE-Bench-CL | continual-learning benchmark | `https://github.com/thomasjoshi/agents-never-forget` | Continual coding-agent benchmark; useful reviewer for trajectory and evidence reuse boundaries. | GitHub discussion/issue only if appropriate | Researcher / Evaluator | candidate |

## First Batch

Start with five targets before scaling:

1. OpenHands
2. SWE-agent / mini-SWE-agent
3. Aider
4. LangGraph
5. SWE-bench

Reason: these are closest to coding-agent evidence and benchmark claims. A
concrete technical review from any one of them is more valuable than sending
weak messages to all 20.

## Tracking Fields To Fill After Sending

| Target | Sent date | Channel URL | Message variant | Reply | Action needed | Outcome |
| --- | --- | --- | --- | --- | --- | --- |
| OpenHands |  |  |  |  |  |  |
| SWE-agent / mini-SWE-agent |  |  |  |  |  |  |
| Aider |  |  |  |  |  |  |
| LangGraph |  |  |  |  |  |  |
| SWE-bench |  |  |  |  |  |  |

## Do Not Say

- Any target endorsed, reviewed, adopted, deployed, or shared the project until
  there is public evidence.
- The project has reached major-star milestones.
- Native Claude/Codex/Cursor/Devin/CI log ingestion is supported.
- Evidence Court proves tests actually ran outside the supplied record.
- OpenMako's broader agent runtime ships in this repository.
