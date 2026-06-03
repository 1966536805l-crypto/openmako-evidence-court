# Evidence Court Capability Gates

This is a claim-promotion index for the public Evidence Court v0.1 release.

The rule is simple: a public claim is allowed only when this repository includes
a runnable command, test, or artifact check that supports it.

## Claim Promotion Matrix

| Capability claim | Current status | Required evidence | Not solved yet |
| --- | --- | --- | --- |
| Evidence Court audits supplied structured JSON agent-run records | v0.1 support | `python -m pytest -p no:cacheprovider tests/test_evidence_court.py -q`; `mako evidence-court --demo bad-run`; `mako evidence-court --demo good-run --json`; `bash scripts/evidence_court_smoke.sh` | Native Claude/Codex/Cursor/Devin/CI log ingestion |
| OpenMako AgentRunResult JSON producer artifacts | v0.1 narrow adapter | `mako evidence-court --from-openmako-agent-run-result tests/fixtures/evidence_court/openmako_agent_run_result_bad.json --json`; fixture returns `FAIL` for missing required pytest and protected test edit | Native vendor log parsing; generic producer schema negotiation |
| Marked transcript v0 conversion | v0.1 narrow adapter | `mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json`; mixed input modes return exit code 2 | Native vendor transcript parsing; duplicate/unclosed marker hardening |
| Explicit Evidence Court JSONL event streams | v0.1 narrow adapter | `mako evidence-court --from-jsonl-events run.events.jsonl --json`; smoke artifact `jsonl-events.json` contains `"verdict": "FAIL"` | Native vendor event extraction; CI log parsing |
| CI failure gate | v0.1 support | `mako evidence-court --demo bad-run --fail-on fail --json` exits 1; `scripts/evidence_court_smoke.sh` checks this path | Proving tests actually ran outside the supplied record |
| Smoke artifact verification | v0.1 support | `bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke`; `bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke` | Remote artifact evidence until GitHub Actions is green for the pushed commit |

## Public Wording Rules

Allowed wording:

- "Evidence Court v0.1 audits supplied structured JSON run records."
- "OpenMako AgentRunResult JSON producer artifacts are supported when the
  supplied schema is `openmako.agent_run_result.v0`."
- "Marked transcript v0 is an explicit marker format, not native vendor log
  parsing."
- "Explicit Evidence Court JSONL event streams are supported when producers
  provide structured events."
- "The smoke artifact verifies report files, expected verdicts, source labels,
  and SHA-256 hashes."

Forbidden wording until the matching gate passes:

- "Native Claude/Codex/Cursor/Devin ingestion is supported."
- "Evidence Court parses raw chat transcripts."
- "Evidence Court parses CI logs."
- "Evidence Court proves tests actually ran in the real world."
- "This repository ships the broader OpenMako coding agent runtime."
- "Desktop, quant trading, planner, or autonomous repair capability is proven by
  this release."

## Release Rule

For every public-facing claim, include:

- What changed.
- What command or artifact proves it.
- What failure mode it reduces.
- What it does not solve.
- The next measurable gate.

If one of those lines is missing, the claim is not ready for public launch.
