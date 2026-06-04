#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

PY="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/openmako_pycache}"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

ARTIFACT_DIR="${EVIDENCE_COURT_ARTIFACT_DIR:-}"
JSONL_EVENTS_FILE="evidence-court-smoke-jsonl-events.jsonl"
cleanup() {
  rm -f "${JSONL_EVENTS_FILE}"
}
trap cleanup EXIT

usage() {
  cat <<'EOF'
Usage:
  bash scripts/evidence_court_smoke.sh [--artifact-dir DIR]

--artifact-dir DIR writes reviewer-facing smoke artifacts to DIR.
EVIDENCE_COURT_ARTIFACT_DIR provides the same setting for CI.
EOF
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --artifact-dir)
      if [[ "$#" -lt 2 || -z "${2:-}" ]]; then
        echo "--artifact-dir requires a directory" >&2
        usage >&2
        exit 2
      fi
      ARTIFACT_DIR="$2"
      shift 2
      ;;
    --artifact-dir=*)
      ARTIFACT_DIR="${1#--artifact-dir=}"
      if [[ -z "${ARTIFACT_DIR}" ]]; then
        echo "--artifact-dir requires a directory" >&2
        usage >&2
        exit 2
      fi
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument for Evidence Court smoke gate: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -n "${ARTIFACT_DIR}" ]]; then
  mkdir -p "${ARTIFACT_DIR}"
fi

echo "[evidence-court-smoke] compile"
"${PY}" -m py_compile quantagent/evidence_court.py quantagent/cli.py tests/test_evidence_court.py

echo "[evidence-court-smoke] focused tests"
"${PY}" -m pytest -p no:cacheprovider tests/test_evidence_court.py -q

echo "[evidence-court-smoke] bad demo must fail"
bad_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --demo bad-run)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${bad_output}" > "${ARTIFACT_DIR}/bad-run.md"
fi
grep -q "## Verdict: FAIL" <<< "${bad_output}"

echo "[evidence-court-smoke] redacted supplied record must fail"
redacted_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${redacted_output}" > "${ARTIFACT_DIR}/redacted-real-world-bad-run.json"
fi
grep -q '"verdict": "FAIL"' <<< "${redacted_output}"
grep -q 'source: examples/evidence-court/redacted-real-world-bad-run.json' <<< "${redacted_output}"
grep -q 'required test not run: python -m pytest tests/test_api_guard.py -q' <<< "${redacted_output}"

echo "[evidence-court-smoke] fail-on gate must block fail verdicts"
set +e
fail_on_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --demo bad-run --fail-on fail --json 2>&1)"
fail_on_code=$?
set -e
if [[ "${fail_on_code}" -ne 1 ]]; then
  echo "expected --fail-on fail to exit 1 for bad-run, got ${fail_on_code}" >&2
  echo "${fail_on_output}" >&2
  exit 1
fi
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${fail_on_output}" > "${ARTIFACT_DIR}/fail-on-fail.json"
fi
grep -q '"verdict": "FAIL"' <<< "${fail_on_output}"

echo "[evidence-court-smoke] reason-code gate must block matching fail codes"
set +e
reason_code_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --demo bad-run --fail-on-reason-code test.required_not_run --json 2>&1)"
reason_code_exit=$?
set -e
if [[ "${reason_code_exit}" -ne 1 ]]; then
  echo "expected --fail-on-reason-code test.required_not_run to exit 1 for bad-run, got ${reason_code_exit}" >&2
  echo "${reason_code_output}" >&2
  exit 1
fi
grep -q '"test.required_not_run"' <<< "${reason_code_output}"

echo "[evidence-court-smoke] reason-code catalog must render"
reason_codes_text="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --list-reason-codes)"
reason_codes_json="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --list-reason-codes --json)"
grep -q 'Evidence Court reason codes:' <<< "${reason_codes_text}"
grep -q 'test.required_not_run' <<< "${reason_codes_text}"
grep -q '"code": "test.required_not_run"' <<< "${reason_codes_json}"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${reason_codes_text}" > "${ARTIFACT_DIR}/reason-codes.md"
  printf '%s\n' "${reason_codes_json}" > "${ARTIFACT_DIR}/reason-codes.json"
fi

echo "[evidence-court-smoke] good demo must pass"
good_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --demo good-run --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${good_output}" > "${ARTIFACT_DIR}/good-run.json"
fi
grep -q '"verdict": "PASS"' <<< "${good_output}"

echo "[evidence-court-smoke] marked transcript must fail closed"
transcript_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${transcript_output}" > "${ARTIFACT_DIR}/marked-transcript.json"
fi
grep -q '"verdict": "FAIL"' <<< "${transcript_output}"

echo "[evidence-court-smoke] OpenMako AgentRunResult must fail closed"
agent_run_result_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --from-openmako-agent-run-result tests/fixtures/evidence_court/openmako_agent_run_result_bad.json --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${agent_run_result_output}" > "${ARTIFACT_DIR}/openmako-agent-run-result.json"
fi
grep -q '"verdict": "FAIL"' <<< "${agent_run_result_output}"
grep -q '"required test not run: python -m pytest tests/test_calculator.py -q"' <<< "${agent_run_result_output}"

cat > "${JSONL_EVENTS_FILE}" <<'JSONL'
{"event":"claimed_task","text":"Fix calculator.add; only calculator.py may be edited."}
{"event":"final_claim","text":"Done. The calculator bug is fixed and tests pass."}
{"event":"file_read","path":"calculator.py"}
{"event":"file_edit","path":"tests/test_calculator.py"}
{"event":"command","command":"python -m py_compile calculator.py"}
{"event":"required_test","command":"python -m pytest tests/test_calculator.py -q"}
JSONL

echo "[evidence-court-smoke] explicit JSONL events must fail closed"
jsonl_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --from-jsonl-events "${JSONL_EVENTS_FILE}" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${jsonl_output}" > "${ARTIFACT_DIR}/jsonl-events.json"
fi
grep -q '"verdict": "FAIL"' <<< "${jsonl_output}"
grep -q '"required test not run: python -m pytest tests/test_calculator.py -q"' <<< "${jsonl_output}"

echo "[evidence-court-smoke] mixed evidence sources must be rejected"
set +e
mixed_output="$("${PY}" -m quantagent.cli --no-trust-prompt evidence-court --input examples/evidence-court/bad-run.json --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --from-jsonl-events "${JSONL_EVENTS_FILE}" 2>&1)"
mixed_code=$?
set -e
rm -f "${JSONL_EVENTS_FILE}"
if [[ "${mixed_code}" -ne 2 ]]; then
  echo "expected mixed input rejection with exit code 2, got ${mixed_code}" >&2
  echo "${mixed_output}" >&2
  exit 1
fi
if [[ -n "${ARTIFACT_DIR}" ]]; then
  {
    printf 'exit_code=%s\n' "${mixed_code}"
    printf '%s\n' "${mixed_output}"
  } > "${ARTIFACT_DIR}/mixed-source-rejection.txt"
fi

echo "[evidence-court-smoke] release set boundary"
if [[ -n "${EVIDENCE_COURT_BRANCH_DIFF_BASE:-}" && ! "${EVIDENCE_COURT_BRANCH_DIFF_BASE}" =~ ^0+$ ]]; then
  bash scripts/evidence_court_release_set.sh --check-branch-diff "${EVIDENCE_COURT_BRANCH_DIFF_BASE}"
else
  bash scripts/evidence_court_release_set.sh --check
fi

echo "[evidence-court-smoke] README boundary claim"
grep -q "does not yet natively ingest Claude Code, Codex, Cursor, Devin, or CI logs" README.md
grep -q "Claim: Done. The calculator bug is fixed and tests pass." README.md
grep -q "Evidence: required test not run: python -m pytest tests/test_calculator.py -q" README.md

if [[ -n "${ARTIFACT_DIR}" ]]; then
  cat > "${ARTIFACT_DIR}/artifact-manifest.json" <<'EOF'
{
  "artifact": "evidence-court-smoke",
  "version": "v0.1",
  "safe_claim": "Evidence Court audits supplied JSON run records, OpenMako AgentRunResult JSON producer artifacts, explicit marked transcript v0 files, and explicit Evidence Court JSONL event streams for claim/evidence/scope/test mismatches.",
  "review_path": [
    "reviewer-quickstart.md",
    "bad-run.md",
    "redacted-real-world-bad-run.json",
    "fail-on-fail.json",
    "reason-codes.json",
    "reason-codes.md",
    "good-run.json",
    "marked-transcript.json",
    "openmako-agent-run-result.json",
    "jsonl-events.json",
    "mixed-source-rejection.txt",
    "smoke-summary.txt"
  ],
  "expected_checks": {
    "bad-run.md": "## Verdict: FAIL",
    "redacted-real-world-bad-run.json": "\"verdict\": \"FAIL\"",
    "fail-on-fail.json": "\"verdict\": \"FAIL\" and command exit code 1",
    "reason-codes.json": "\"code\": \"test.required_not_run\"",
    "reason-codes.md": "test.required_not_run",
    "good-run.json": "\"verdict\": \"PASS\"",
    "marked-transcript.json": "\"verdict\": \"FAIL\"",
    "openmako-agent-run-result.json": "\"verdict\": \"FAIL\"",
    "jsonl-events.json": "\"verdict\": \"FAIL\"",
    "mixed-source-rejection.txt": "exit_code=2",
    "smoke-summary.txt": "Evidence Court smoke gate passed."
  },
  "source_provenance_checks": {
    "bad-run.md": "source: bad-run-demo",
    "redacted-real-world-bad-run.json": "source: examples/evidence-court/redacted-real-world-bad-run.json",
    "fail-on-fail.json": "source: bad-run-demo",
    "good-run.json": "source: good-run-demo",
    "marked-transcript.json": "source: tests/fixtures/evidence_court/marked_bad_transcript.txt",
    "openmako-agent-run-result.json": "source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
    "jsonl-events.json": "source: evidence-court-smoke-jsonl-events.jsonl"
  },
  "ci_policy_recipe": {
    "required_test_gate": "mako evidence-court --input <run-record.json> --fail-on-reason-code test.required_not_run --json",
    "effect": "exits 1 when the supplied record omits the required test command"
  },
  "boundaries": [
    "No native Claude/Codex/Cursor/Devin/CI log ingestion claim.",
    "No proof that tests ran outside the supplied record.",
    "No broad SWE repair, unknown NPM reasoning, or Desktop L4/L5 autonomy claim."
  ]
}
EOF
  cat > "${ARTIFACT_DIR}/reviewer-quickstart.md" <<'EOF'
# Evidence Court Smoke Artifact

Evidence Court is not another coding agent. It is a claim-vs-evidence gate for supplied agent-run records.

## 30-Second Review Path

1. Open `artifact-manifest.json`: it lists the safe claim, review files, expected checks, source provenance checks, artifact file SHA-256 hashes, and boundaries.
2. Open `bad-run.md` first: the agent claims success, but Evidence Court returns `FAIL` because the supplied run record reports a protected test edit and does not report the required pytest command. Confirm it includes `source: bad-run-demo`.
3. Open `redacted-real-world-bad-run.json`: a redacted supplied record returns `"verdict": "FAIL"` because it reports protected edits and does not report the required API guard pytest. Confirm it includes `source: examples/evidence-court/redacted-real-world-bad-run.json`.
4. Open `fail-on-fail.json`: the same bad run is executed with `--fail-on fail`, and the smoke gate only writes this artifact after the command exits with code 1.
5. Open `reason-codes.json` or `reason-codes.md`: the artifact includes the exact machine-readable reason-code catalog used by `--fail-on-reason-code`.
6. Open `good-run.json`: the supplied run record stays in scope, reports the required pytest command, returns `"verdict": "PASS"`, and includes `source: good-run-demo`.
7. Open `marked-transcript.json`: explicit marked transcript v0 input returns `"verdict": "FAIL"` and includes the fixture path as `source`.
8. Open `openmako-agent-run-result.json`: explicit OpenMako AgentRunResult input returns `"verdict": "FAIL"` and includes the fixture path as `source`.
9. Open `jsonl-events.json`: explicit Evidence Court JSONL event stream input returns `"verdict": "FAIL"` and includes `source: evidence-court-smoke-jsonl-events.jsonl`.
10. Open `mixed-source-rejection.txt`: mixed JSON plus transcript plus JSONL inputs fail closed with `exit_code=2`.
11. Open `smoke-summary.txt`: the smoke gate reports `Evidence Court smoke gate passed.`

This artifact shows these fixtures: `bad-run` fails, redacted supplied-record bad run fails, `good-run` passes, marked transcript v0 input fails closed, OpenMako AgentRunResult input fails closed, explicit JSONL event input fails closed, and mixed input modes are rejected.

## CI Policy Recipe

To block one concrete failure class instead of parsing prose, run:

```bash
mako evidence-court --input <run-record.json> --fail-on-reason-code test.required_not_run --json
```

This exits 1 when the supplied record contains `test.required_not_run`. It still audits only the supplied record; it does not rerun tests or parse native CI logs.

## Boundary

This artifact shows the smoke gate output for supplied JSON, OpenMako AgentRunResult producer artifacts, marked transcript v0, and explicit Evidence Court JSONL event records. It does not prove native Claude/Codex/Cursor/Devin/CI log ingestion, and it does not prove tests really ran outside the supplied record.

It does not prove broad SWE repair, unknown NPM reasoning, or Desktop L4/L5 autonomy.

Safe claim: Evidence Court v0.1 audits supplied JSON run records, OpenMako AgentRunResult JSON producer artifacts, explicit marked transcript v0 files, and explicit Evidence Court JSONL event streams for claim/evidence/scope/test mismatches.
EOF
  cat > "${ARTIFACT_DIR}/smoke-summary.txt" <<'EOF'
Evidence Court smoke gate passed.
artifact-manifest.json lists the safe claim and expected review checks.
artifact-manifest.json lists source provenance checks for every generated report.
artifact-manifest.json lists SHA-256 hashes for every file in the review path.
reviewer-quickstart.md gives the 30-second review path.
compile gate passed for quantagent/evidence_court.py, quantagent/cli.py, and focused tests.
focused tests passed for tests/test_evidence_court.py.
demo verdict gate checked bad-run FAIL and good-run PASS.
redacted supplied-record gate checked redacted-real-world-bad-run FAIL.
fail-on gate checked bad-run exits 1 with --fail-on fail.
reason-code gate checked bad-run exits 1 with --fail-on-reason-code test.required_not_run.
reason-code catalog gate checked --list-reason-codes text and JSON output.
input-mode gate checked marked transcript FAIL, OpenMako AgentRunResult FAIL, explicit JSONL events FAIL, and mixed JSON plus transcript plus JSONL rejection.
release boundary gate checked the Evidence Court release set.
bad-run.md must contain Verdict: FAIL.
redacted-real-world-bad-run.json must contain "verdict": "FAIL".
fail-on-fail.json must contain "verdict": "FAIL" and is only written after exit code 1.
good-run.json must contain "verdict": "PASS".
marked-transcript.json must contain "verdict": "FAIL".
openmako-agent-run-result.json must contain "verdict": "FAIL".
jsonl-events.json must contain "verdict": "FAIL".
report artifacts must contain source provenance in their Evidence section.
reason-codes.json and reason-codes.md must list test.required_not_run.
review-path artifacts must have SHA-256 hashes in artifact-manifest.json.
mixed-source-rejection.txt must show exit_code=2.
EOF
  "${PY}" - "${ARTIFACT_DIR}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

artifact_dir = Path(sys.argv[1])
manifest_path = artifact_dir / "artifact-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["artifact_file_sha256"] = {
    name: hashlib.sha256((artifact_dir / name).read_bytes()).hexdigest()
    for name in manifest["review_path"]
}
manifest_path.write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
fi

echo "Evidence Court smoke gate passed."
