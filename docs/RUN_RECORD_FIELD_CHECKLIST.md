# Run-Record Field Checklist

This checklist is for reviewers and adapter authors who want to turn a
terminal, local-gateway, benchmark, or agent-framework run into an explicit
Evidence Court supplied record.

It is guidance, not evidence of native ingestion, endorsement, adoption,
integration, or review by any external project.

## Minimum Fields

A supportable "done/tests passed" claim should include:

- `final_claim`: the exact final success claim being audited.
- `claimed_task` or `claim`: the requested task boundary.
- `files_read`: files the run says the agent inspected before editing.
- `files_edited`: files the run says the agent changed.
- `commands_run`: exact commands the run reports, preferably with exit status
  and output attached to each command object.
- `test_output`: supplied test output if the run reports test success or
  failure.
- `required_tests` or `required_commands`: commands a reviewer expects before
  the claim is supportable.
- `allowed_edit_paths` or `allowed_files`: the intended edit boundary.
- `protected_paths`: files or directories whose edits should be suspicious
  without explicit scope.
- `source`: provenance label for the supplied record or generated artifact.

## Trend-Pressure Metadata

Local agent gateways, terminal agents, benchmark harnesses, and internal coding
agents increasingly expose tool calls, permission boundaries, sandboxes, and
artifact URLs. Include these fields when available, but do not treat them as
proof until evaluator logic exists:

- `agent_runtime`: runtime label such as terminal agent, local gateway, web IDE,
  benchmark harness, or internal coding agent.
- `tool_calls`: summarized tool calls or shell steps, if separate from
  `commands_run`.
- `approval_events`: approvals or denials around risky tool calls or protected
  writes.
- `sandbox_boundary`: sandbox mode, network policy, or filesystem boundary
  reported by the producing agent.
- `diff_summary`: compact changed-file and protected-path summary.
- `artifact_urls`: public PR, CI, or artifact URLs used for remote review.
- `redaction_note`: what was removed before sharing the record.

## Reviewer Questions

Use these questions before accepting a final success claim:

1. Does the record include the exact required test or eval command?
2. Does passing output match the command that was required?
3. Did the run edit protected tests, fixtures, lockfiles, CI, docs, or config
   outside the stated task scope?
4. Does the final claim go beyond the supplied record?
5. Are approval and sandbox fields only context, or are they being overclaimed
   as proof?
6. Are public artifact URLs fresh enough to verify, or could they be stale?

## Current Evidence Court Boundary

Evidence Court v0.1 preserves supported metadata fields for reviewer context,
but only its claim/evidence/scope/test logic affects the verdict. Metadata
fields do not prove sandboxing, approvals, native log ingestion, real test
execution, external review, adoption, endorsement, or share readiness.

For protected-path edits, Evidence Court can emit narrow metadata-gap reason
codes when the supplied record omits approval or sandbox-boundary context:

- `approval.protected_edit_missing`: a protected path was edited without
  supplied positive approval evidence for that path.
- `sandbox.boundary_missing_for_protected_edit`: a protected path was edited
  without supplied sandbox-boundary metadata.

These codes do not verify real approvals, real sandbox enforcement, native log
ingestion, or runtime behavior outside the supplied record. They only make the
missing approval/sandbox boundary explicit for reviewers and CI wrappers.

Evidence Court v0.1 does not natively ingest Hermes Agent, OpenClaw, opencode,
OpenHands, SWE-agent, Aider, Open SWE, LangGraph, Claude, Codex, Cursor, Devin,
GitHub Actions, or CI logs. Those would need separate adapters and tests before
the project can claim native support.

## Example CI Gate

Use exact reason-code gating when the required test command is the key boundary:

```bash
mako evidence-court --input <run-record.json> --fail-on-reason-code test.required_not_run --json
```

This exits 1 only when the supplied record omits the required test command. It
does not independently rerun tests or inspect external logs.
