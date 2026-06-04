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

## Hot Trend Ranking

This ranking is a build-order input, not a market-size claim.

| Rank | Trend | Why it matters now | Evidence Court development response |
| --- | --- | --- | --- |
| 1 | Local agent gateways and terminal coding agents are converging around command history, tool calls, and final claims. | Hermes, OpenClaw, opencode, Aider, and OpenHands-style workflows all need a compact way to hand off what happened after a run. | Make the supplied-record checklist the primary integration surface before attempting native adapters. |
| 2 | Human approval, sandbox, and permission boundaries are becoming part of the product surface. | Local agents increasingly expose risky-action controls, but a final "done" claim rarely explains whether a risky step was approved or sandboxed. | Add metadata guidance for `approval_events`, `sandbox_boundary`, and `tool_calls`; do not treat those fields as proof until evaluator logic exists. |
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

## Next Development Slice

Build the next slice as synthetic supplied-record coverage, not as a native
adapter claim:

1. `terminal-agent-bad-run.json`: command-history style record with a final
   tests-passed claim, protected test edit, and missing required test command.
2. `local-gateway-bad-run.json`: gateway-style record with `tool_calls`,
   `approval_events`, and `sandbox_boundary` metadata, but still missing the
   required test command.
3. Focused test expectation: both records must produce the existing
   `test.required_not_run` reason code; extra gateway metadata must not be
   misrepresented as sandbox proof.
4. Public wording gate: describe these as synthetic supplied-record examples
   only, not Hermes/OpenClaw/opencode/OpenHands/Aider native ingestion.

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
