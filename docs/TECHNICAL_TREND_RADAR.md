# Technical Trend Radar

Observed on 2026-06-04 from public project pages. This is a development input,
not evidence of endorsement, adoption, integration, or review.

## What Is Moving

| Project | Public source | Trend signal | Evidence Court development pressure |
| --- | --- | --- | --- |
| Hermes Agent | `https://github.com/NousResearch/hermes-agent` | Local agent gateway with subagents, memory, multi-channel entry points, and multiple coding-agent backends. | Keep Evidence Court as a post-run supplied-record auditor that can receive a small handoff artifact from fast local-agent sessions. |
| OpenClaw | `https://github.com/openclaw/openclaw` | Local-first coding-agent workflow with gateway, sandbox, approvals, and human-controlled execution themes. | Keep explicit approval/sandbox boundary fields visible and flag missing supplied metadata around protected-path edits. |
| opencode | `https://github.com/sst/opencode` | Terminal/TUI coding-agent workflow where command history and final claims are close together. | Make the reason-code CI recipe obvious for terminal users: missing required test command should fail with a stable machine-readable reason. |
| OpenHands | `https://github.com/OpenHands/OpenHands` | Software-development agent platform with local, CLI, SDK, and evaluation-facing workflows. | Use the standalone run-record field checklist to map commands, edits, tests, protected paths, and final claims without claiming native ingestion. |
| SWE-agent / mini-SWE-agent | `https://github.com/SWE-agent/mini-swe-agent` | Small linear trajectory agent and SWE-Bench-oriented evaluation flow. | Treat exact eval command, patch scope, protected-file edits, and supplied output as first-class evidence fields. |
| Aider | `https://github.com/Aider-AI/aider` | Terminal pair-programming agent centered on local git edits, tests, and lint commands. | Keep the record shape friendly to terminal sessions: command list, edited files, diff/protected-path summary, test output status, and final claim. |

## Hot Trend Ranking

This ranking is a build-order input, not a market-size claim.

| Rank | Trend | Why it matters now | Evidence Court development response |
| --- | --- | --- | --- |
| 1 | Local agent gateways and terminal coding agents are converging around command history, tool calls, and final claims. | Hermes, OpenClaw, opencode, Aider, and OpenHands-style workflows all need a compact way to hand off what happened after a run. | Make the supplied-record checklist the primary integration surface before attempting native adapters. |
| 2 | Human approval, sandbox, and permission boundaries are becoming part of the product surface. | Local agents increasingly expose risky-action controls, but a final "done" claim rarely explains whether a risky step was approved or sandboxed. | Preserve `approval_events`, `sandbox_boundary`, and `tool_calls`; emit narrow metadata-gap reason codes for protected-path edits when approval or sandbox-boundary context is missing. |
| 3 | CI and benchmark communities need machine-readable failure categories, not prose-only verdicts. | A terminal user can understand a FAIL line, but CI wrappers need stable categories like `test.required_not_run`. | Keep exact reason-code gates prominent and avoid adding fuzzy "agent quality" scores. |
| 4 | Trace and artifact exports are safer than vendor-log scraping for v0.1. | Native logs differ by product and can change quickly; explicit exports let reviewers see the source boundary. | Prefer explicit JSON/JSONL/marked-record examples and reviewer artifacts over native Hermes/OpenClaw/opencode parsers. |
| 5 | Public proof artifacts matter more than broad claims. | Reviewers can verify a digest, artifact file, and reason-code command faster than they can audit a broad autonomy claim. | Keep proof cards, artifact manifests, SHA-256 hashes, and stale-proof warnings in the launch path. |

## Product Bet

Evidence Court should not compete with these projects as another coding agent.
The narrow opportunity is a claim-vs-evidence layer that receives explicit
records from agent sessions and says whether the record supports the final
"done/tests passed" claim.

## Near-Term Development Bets

1. Adapter handoff contract: keep `examples/evidence-court/run-record.schema.json`
   permissive, but document the minimum useful fields for terminal and
   local-agent sessions.
2. Approval/sandbox boundary reason codes: keep
   `approval.protected_edit_missing` and
   `sandbox.boundary_missing_for_protected_edit` narrow to protected-path edits
   reported in the supplied record; do not expand them into real sandbox proof.
3. Terminal-agent CI path: keep
   `--fail-on-reason-code test.required_not_run` as the first public CI recipe,
   then add one more recipe only after a reviewer confirms the wording is clear.
4. Trace samples, not native parsers: add generic supplied-record examples for a
   terminal agent and a local gateway session before attempting native adapters.
5. Public review before scaling outreach: ask Hermes/OpenClaw/opencode style
   projects for boundary criticism only after PR-head CI or a first-batch reply.

## Next Development Slice

Build the next slice as synthetic supplied-record coverage, not as a native
adapter claim:

1. `terminal-agent-bad-run.json`: command-history style record with a final
   tests-passed claim, protected test edit, and missing required test command.
2. `local-gateway-bad-run.json`: gateway-style record with `tool_calls`,
   `approval_events`, and `sandbox_boundary` metadata, but still missing the
   required test command.
3. Focused test expectation: both records must produce the existing
   `test.required_not_run` reason code; protected-path edits with missing
   approval/sandbox context must produce explicit metadata-gap reason codes;
   extra gateway metadata must not be misrepresented as sandbox proof.
4. Public wording gate: describe these as synthetic supplied-record examples
   only, not Hermes/OpenClaw/opencode/OpenHands/Aider native ingestion.

## Run-Record Field Checklist

The reviewer-facing checklist now lives in
`docs/RUN_RECORD_FIELD_CHECKLIST.md`. It translates the trend signals above into
supplied-record fields such as `final_claim`, `commands_run`,
`required_tests`, `allowed_edit_paths`, `protected_paths`, `approval_events`,
`sandbox_boundary`, and `artifact_urls` without claiming native ingestion of
any external agent log.

Evidence Court v0.1 preserves supported metadata fields for reviewer context,
but only its claim/evidence/scope/test logic affects the verdict. Metadata
fields do not prove sandboxing, approvals, native log ingestion, real test
execution, external review, adoption, endorsement, or share readiness.
Protected-path edits can now surface missing approval or sandbox-boundary
context as explicit reason codes; those codes still do not prove real approval
or real sandbox enforcement.

## Trend-To-Mechanism Map

| Trend | Small mechanism to build now | What to skip |
| --- | --- | --- |
| Local gateway and subagent workflows | Preserve `source`, `agent_runtime`, and explicit record provenance. | Do not parse native Hermes/OpenClaw logs yet. |
| Human approval and sandbox themes | Ask producers to include `approval_events` and `sandbox_boundary` metadata; flag protected-path edits when that context is missing. | Do not claim sandbox proof from supplied text. |
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

Use `docs/RUN_RECORD_FIELD_CHECKLIST.md` as the next technical-review handoff.
Do not build native Hermes/OpenClaw/opencode/OpenHands/Aider adapters until an
external reviewer confirms the supplied-record fields are clear enough.
