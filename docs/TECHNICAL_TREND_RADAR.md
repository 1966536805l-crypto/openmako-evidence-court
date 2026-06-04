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

## Run-Record Field Checklist

This is the current checklist for adapter authors and reviewers. It translates
the trend signals above into supplied-record fields without claiming native
ingestion of any external agent log.

Minimum useful fields for a supportable "done/tests passed" claim:

- `final_claim`: the exact final success claim being audited.
- `claimed_task` or `claim`: the requested task boundary.
- `files_read`: files the agent says it inspected before editing.
- `files_edited`: files the agent says it changed.
- `commands_run`: exact commands the agent says it ran, preferably with exit
  status and output attached to each command object.
- `test_output`: supplied test output if the run reports test success or
  failure.
- `required_tests` or `required_commands`: commands the reviewer expects before
  the claim is supportable.
- `allowed_edit_paths` or `allowed_files`: the intended edit boundary.
- `protected_paths`: files or directories whose edits should be treated as
  suspicious without explicit scope.
- `source`: provenance label for the supplied record or generated artifact.

Trend-pressure fields to include as explicit metadata when available:

- `agent_runtime`: human-readable runtime label such as terminal agent, local
  gateway, web IDE, or benchmark harness.
- `tool_calls`: summarized tool calls or shell steps, if separate from
  `commands_run`.
- `approval_events`: approvals or denials around risky tool calls or protected
  writes.
- `sandbox_boundary`: sandbox mode, network policy, or filesystem boundary
  reported by the producing agent.
- `diff_summary`: compact changed-file and protected-path summary.
- `artifact_urls`: public PR, CI, or artifact URLs when the record is being used
  for remote review.
- `redaction_note`: what was removed before sharing the record.

Evidence Court v0.1 only evaluates the fields its current loader understands.
Extra checklist fields are supplied metadata for reviewers and future adapters;
they do not prove sandboxing, approvals, native log ingestion, real test
execution, or external review.

## Trend-To-Mechanism Map

| Trend | Small mechanism to build now | What to skip |
| --- | --- | --- |
| Local gateway and subagent workflows | Preserve `source`, `agent_runtime`, and explicit record provenance. | Do not parse native Hermes/OpenClaw logs yet. |
| Human approval and sandbox themes | Ask producers to include `approval_events` and `sandbox_boundary` metadata. | Do not claim sandbox proof from supplied text. |
| Terminal/TUI coding agents | Keep exact `commands_run`, `required_tests`, and reason-code CI examples visible. | Do not add broad terminal-agent adapters before reviewer feedback. |
| SWE-Bench and eval workflows | Require task boundary, patch scope, commands, and supplied output in one record. | Do not claim benchmark performance from a single smoke fixture. |
| Public launch and outreach pressure | Use public PR-head CI and artifact URLs before asking for broader attention. | Do not optimize for stars before technical boundary review. |

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

Keep the checklist in this radar until a public PR-head CI artifact exists or an
external reviewer asks for a standalone checklist. If that happens, split this
section into `docs/RUN_RECORD_FIELD_CHECKLIST.md` and keep the same boundaries.
