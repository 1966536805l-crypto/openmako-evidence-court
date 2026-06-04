# Technical Trend Radar

Observed on 2026-06-04 from public project pages. This is a development input,
not evidence of endorsement, adoption, integration, or review.

## What Is Moving

| Project | Public source | Trend signal | Evidence Court development pressure |
| --- | --- | --- | --- |
| Hermes Agent | `https://github.com/NousResearch/hermes-agent` | Local agent gateway with subagents, memory, multi-channel entry points, and multiple coding-agent backends. | Keep Evidence Court as a post-run supplied-record auditor that can receive a small handoff artifact from fast local-agent sessions. |
| OpenClaw | `https://github.com/openclaw/openclaw` | Local-first coding-agent workflow with gateway, sandbox, approvals, and human-controlled execution themes. | Add explicit approval/sandbox boundary fields before any final success claim is treated as supportable. |
| opencode | `https://github.com/sst/opencode` | Terminal/TUI coding-agent workflow where command history and final claims are close together. | Make the reason-code CI recipe obvious for terminal users: missing required test command should fail with a stable machine-readable reason. |
| OpenHands | `https://github.com/OpenHands/OpenHands` | Software-development agent platform with local, CLI, SDK, and evaluation-facing workflows. | Publish a minimal run-record field checklist that maps commands, edits, tests, protected paths, and final claims without claiming native ingestion. |
| SWE-agent / mini-SWE-agent | `https://github.com/SWE-agent/mini-swe-agent` | Small linear trajectory agent and SWE-Bench-oriented evaluation flow. | Treat exact eval command, patch scope, protected-file edits, and supplied output as first-class evidence fields. |
| Aider | `https://github.com/Aider-AI/aider` | Terminal pair-programming agent centered on local git edits, tests, and lint commands. | Keep the record shape friendly to terminal sessions: command list, edited files, diff/protected-path summary, test output status, and final claim. |

## Product Bet

Evidence Court should not compete with these projects as another coding agent.
The narrow opportunity is a claim-vs-evidence layer that receives explicit
records from agent sessions and says whether the record supports the final
"done/tests passed" claim.

## Near-Term Development Bets

1. Adapter handoff contract: keep `examples/evidence-court/run-record.schema.json`
   permissive, but document the minimum useful fields for terminal and
   local-agent sessions.
2. Approval boundary reason codes: add future reason codes for missing approval
   evidence before protected writes, unsafe sandbox gaps, or untracked command
   execution claims.
3. Terminal-agent CI path: keep
   `--fail-on-reason-code test.required_not_run` as the first public CI recipe,
   then add one more recipe only after a reviewer confirms the wording is clear.
4. Trace samples, not native parsers: add generic supplied-record examples for a
   terminal agent and a local gateway session before attempting native adapters.
5. Public review before scaling outreach: ask Hermes/OpenClaw/opencode style
   projects for boundary criticism only after PR-head CI or a first-batch reply.

## Boundaries

- No project listed here has endorsed, reviewed, adopted, integrated, or shared
  Evidence Court unless a public evidence URL is added elsewhere.
- Evidence Court v0.1 does not natively ingest Hermes, OpenClaw, opencode,
  OpenHands, SWE-agent, Aider, Claude, Codex, Cursor, Devin, or CI logs.
- These trends do not prove broader SWE repair, autonomous coding ability,
  benchmark performance, launch readiness, star growth, or repost likelihood.
- This radar does not replace `docs/OUTREACH_TARGETS.md`; it explains why the
  outreach asks should stay technical and bounded.

## Smallest Next Mechanism

Add a `docs/RUN_RECORD_FIELD_CHECKLIST.md` only after the current reason-code
branch has a public PR-head CI artifact or an external reviewer asks for the
schema in checklist form. Until then, the safer improvement is to keep the schema
handoff and reason-code CI recipe small and reviewable.
