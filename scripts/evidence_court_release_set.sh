#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"
PY="${PYTHON:-python3}"

INCLUDE_PATHS=(
  ".github/ISSUE_TEMPLATE/technical-review-request.md"
  ".github/workflows/evidence-court.yml"
  "LICENSE"
  "README.md"
  "pyproject.toml"
  "docs/CAPABILITY_GATES.md"
  "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md"
  "docs/EVIDENCE_COURT_V0_1_PR_BODY.md"
  "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md"
  "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md"
  "docs/EVIDENCE_COURT_COMPARISON.md"
  "docs/TECHNICAL_TREND_RADAR.md"
  "docs/REDACTION_GUIDE.md"
  "docs/CURRENT_PROOF_STATUS.md"
  "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md"
  "docs/EXPERT_REVIEW_BRIEF.md"
  "docs/OUTREACH.md"
  "docs/OUTREACH_TARGETS.md"
  "docs/TECHNICAL_REVIEW_REQUEST.md"
  "docs/PUBLIC_PROOF.md"
  "docs/demo-terminal.svg"
  "docs/LAUNCH_POST.md"
  "docs/social-card.svg"
  "docs/RELEASE_NOTES_V0_1_0.md"
  "docs/RELEASE_NOTES_V0_1_1.md"
  "docs/RELEASE_NOTES_V0_1_2.md"
  "examples/evidence-court/bad-run.json"
  "examples/evidence-court/bad-run.report.json"
  "examples/evidence-court/good-run.json"
  "examples/evidence-court/local-gateway-bad-run.json"
  "examples/evidence-court/redacted-real-world-bad-run.json"
  "examples/evidence-court/run-record.schema.json"
  "examples/evidence-court/terminal-agent-bad-run.json"
  "quantagent/evidence_court.py"
  "quantagent/__init__.py"
  "quantagent/cli.py"
  "scripts/evidence_court_release_set.sh"
  "scripts/evidence_court_smoke.sh"
  "tests/fixtures/evidence_court/marked_bad_transcript.txt"
  "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json"
  "tests/fixtures/evidence_court/test_outputs/runner_outputs.json"
  "tests/test_evidence_court.py"
  "tests/test_evidence_court_smoke_script.py"
)

EXCLUDE_PATHS=(
  "quantagent/agent_planner.py"
  "tests/test_agent_planner_contract.py"
  "tests/test_external_benchmark_multimodule_regression.py"
)

usage() {
  cat <<'EOF'
Usage:
  bash scripts/evidence_court_release_set.sh --check
  bash scripts/evidence_court_release_set.sh --check-staged-release-set
  bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy
  bash scripts/evidence_court_release_set.sh --check-branch-diff [BASE_REF]
  bash scripts/evidence_court_release_set.sh --verify-artifact-dir DIR
  bash scripts/evidence_court_release_set.sh --list

--check verifies that release files exist and that any staged files are limited
to the Evidence Court v0.1 release set plus optional PROGRESS.md bookkeeping.
--check-staged-release-set additionally requires every release file to be
staged and no extra files; use it immediately before committing the Evidence
Court v0.1 PR. PROGRESS.md is allowed only by --check, not by this exact gate.
--audit-staged-claim-copy checks staged public copy for required claim
boundaries after --check-staged-release-set passes.
--check-branch-diff verifies that committed branch changes against BASE_REF
are limited to the Evidence Court v0.1 release set. BASE_REF defaults to main.
--verify-artifact-dir verifies a downloaded or local evidence-court-smoke
artifact directory, including review-path files, expected verdict/source text,
and SHA-256 hashes recorded in artifact-manifest.json.
EOF
}

contains_path() {
  local needle="$1"
  shift
  local path
  for path in "$@"; do
    [[ "${path}" == "${needle}" ]] && return 0
  done
  return 1
}

list_paths() {
  echo "Evidence Court v0.1 include paths:"
  printf '  %s\n' "${INCLUDE_PATHS[@]}"
  echo
  echo "Excluded from Evidence Court v0.1 claim:"
  printf '  %s\n' "${EXCLUDE_PATHS[@]}"
}

check_paths_exist() {
  local missing=0
  local path
  for path in "${INCLUDE_PATHS[@]}"; do
    if [[ ! -e "${path}" ]]; then
      echo "missing release file: ${path}" >&2
      missing=1
    fi
  done
  return "${missing}"
}

check_staged_files() {
  local invalid=0
  local staged_count=0
  local path
  while IFS= read -r path; do
    [[ -z "${path}" ]] && continue
    staged_count=$((staged_count + 1))
    if contains_path "${path}" "${EXCLUDE_PATHS[@]}"; then
      echo "excluded file is staged for Evidence Court v0.1: ${path}" >&2
      invalid=1
      continue
    fi
    if [[ "${path}" == "PROGRESS.md" ]]; then
      continue
    fi
    if ! contains_path "${path}" "${INCLUDE_PATHS[@]}"; then
      echo "unexpected staged file for Evidence Court v0.1: ${path}" >&2
      invalid=1
    fi
  done < <(git diff --cached --name-only)

  if [[ "${staged_count}" -eq 0 ]]; then
    echo "No staged files."
    echo "Stage the Evidence Court v0.1 release set with:"
    printf 'git add --'
    printf ' %q' "${INCLUDE_PATHS[@]}" "PROGRESS.md"
    printf '\n'
    return 0
  fi

  if [[ "${invalid}" -eq 0 ]]; then
    echo "Staged files are within the Evidence Court v0.1 release set."
  fi
  return "${invalid}"
}

check_staged_release_set() {
  local invalid=0
  local staged_count=0
  local staged_paths=()
  local path
  while IFS= read -r path; do
    [[ -z "${path}" ]] && continue
    staged_count=$((staged_count + 1))
    staged_paths+=("${path}")
    if contains_path "${path}" "${EXCLUDE_PATHS[@]}"; then
      echo "excluded file is staged for Evidence Court v0.1: ${path}" >&2
      invalid=1
      continue
    fi
    if [[ "${path}" == "PROGRESS.md" ]]; then
      echo "PROGRESS.md is not allowed in the exact Evidence Court v0.1 staged release set; update it separately." >&2
      invalid=1
      continue
    fi
    if ! contains_path "${path}" "${INCLUDE_PATHS[@]}"; then
      echo "unexpected staged file for Evidence Court v0.1: ${path}" >&2
      invalid=1
    fi
  done < <(git diff --cached --name-only)

  for path in "${INCLUDE_PATHS[@]}"; do
    if [[ "${staged_count}" -eq 0 ]] || ! contains_path "${path}" "${staged_paths[@]}"; then
      echo "missing staged release file for Evidence Court v0.1: ${path}" >&2
      invalid=1
    fi
  done

  if [[ "${invalid}" -eq 0 ]]; then
    echo "Staged files exactly cover the Evidence Court v0.1 release set."
  fi
  return "${invalid}"
}

require_staged_contains() {
  local path="$1"
  local needle="$2"
  if ! grep -Fq -- "${needle}" < <(git show ":${path}"); then
    echo "staged claim-copy audit missing in ${path}: ${needle}" >&2
    return 1
  fi
  return 0
}

audit_staged_claim_copy() {
  local invalid=0
  require_staged_contains "README.md" "does not yet natively ingest" || invalid=1
  require_staged_contains "README.md" "Claude Code, Codex, Cursor, Devin, or CI logs" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md" 'Remote CI evidence requires GitHub Actions `Evidence Court Smoke` green for the PR head commit.' || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_PR_BODY.md" "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_PR_BODY.md" "examples/evidence-court/run-record.schema.json" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_PR_BODY.md" "docs/TECHNICAL_TREND_RADAR.md" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_PR_BODY.md" "not evidence of endorsement, adoption, integration, or review" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_PR_BODY.md" "This PR does not claim native Claude/Codex/Cursor/Devin/CI log ingestion" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md" "workflow wired locally" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md" "Only these release files support" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_COMPARISON.md" "Evidence Court only audits the supplied record" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_COMPARISON.md" "does not prove tests actually ran outside" || invalid=1
  require_staged_contains "docs/EVIDENCE_COURT_COMPARISON.md" "does not natively ingest Claude/Codex/Cursor/Devin/CI logs" || invalid=1
  require_staged_contains "docs/TECHNICAL_TREND_RADAR.md" "not evidence of endorsement, adoption, integration, or review" || invalid=1
  require_staged_contains "docs/TECHNICAL_TREND_RADAR.md" "does not natively ingest Hermes, OpenClaw, opencode" || invalid=1
  require_staged_contains "docs/REDACTION_GUIDE.md" "Evidence Court only audits the supplied record" || invalid=1
  require_staged_contains "docs/REDACTION_GUIDE.md" "does not prove tests actually ran outside" || invalid=1
  require_staged_contains "docs/REDACTION_GUIDE.md" "not native Claude/Codex/Cursor/Devin/CI" || invalid=1
  require_staged_contains "docs/CURRENT_PROOF_STATUS.md" "Remote CI evidence is confirmed for proof anchor commit" || invalid=1
  require_staged_contains "docs/CURRENT_PROOF_STATUS.md" "sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac" || invalid=1
  require_staged_contains "docs/CURRENT_PROOF_STATUS.md" "does not prove the latest main commit" || invalid=1
  require_staged_contains "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md" "not an endorsement request" || invalid=1
  require_staged_contains "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md" "Do not treat this draft as a sent review request" || invalid=1
  require_staged_contains "docs/EXPERT_REVIEW_BRIEF.md" "Do Not Share If" || invalid=1
  require_staged_contains "docs/OUTREACH.md" "Do Not Say" || invalid=1
  require_staged_contains "docs/OUTREACH.md" "does not natively ingest Claude/Codex/Cursor/CI logs" || invalid=1
  require_staged_contains "docs/OUTREACH_TARGETS.md" "None of these people, projects, or organizations has endorsed" || invalid=1
  require_staged_contains "docs/OUTREACH_TARGETS.md" "Start with five targets before scaling" || invalid=1
  require_staged_contains "docs/TECHNICAL_REVIEW_REQUEST.md" "not an endorsement request" || invalid=1
  require_staged_contains "docs/TECHNICAL_REVIEW_REQUEST.md" "Review Questions" || invalid=1
  require_staged_contains ".github/ISSUE_TEMPLATE/technical-review-request.md" "not an endorsement request" || invalid=1
  require_staged_contains ".github/ISSUE_TEMPLATE/technical-review-request.md" "Review Questions" || invalid=1
  require_staged_contains "docs/EXPERT_REVIEW_BRIEF.md" "does not provide proof that tests actually ran outside" || invalid=1
  require_staged_contains "docs/PUBLIC_PROOF.md" "What This Does Not Prove" || invalid=1
  require_staged_contains "docs/PUBLIC_PROOF.md" "Artifact digest" || invalid=1
  if [[ "${invalid}" -eq 0 ]]; then
    echo "Staged Evidence Court public claim copy keeps the v0.1 boundaries."
  fi
  return "${invalid}"
}

check_branch_diff() {
  local base_ref="${1:-${EVIDENCE_COURT_BASE_REF:-main}}"
  local invalid=0
  local diff_count=0
  local path

  if ! git rev-parse --verify "${base_ref}^{commit}" >/dev/null 2>&1; then
    echo "base ref not found for Evidence Court branch diff: ${base_ref}" >&2
    return 2
  fi

  while IFS= read -r path; do
    [[ -z "${path}" ]] && continue
    diff_count=$((diff_count + 1))
    if contains_path "${path}" "${EXCLUDE_PATHS[@]}"; then
      echo "excluded file is in branch diff for Evidence Court v0.1: ${path}" >&2
      invalid=1
      continue
    fi
    if ! contains_path "${path}" "${INCLUDE_PATHS[@]}"; then
      echo "unexpected branch diff for Evidence Court v0.1: ${path}" >&2
      invalid=1
    fi
  done < <(git diff --name-only "${base_ref}...HEAD")

  if [[ "${invalid}" -eq 0 ]]; then
    if [[ "${diff_count}" -eq 0 ]]; then
      echo "Branch diff against ${base_ref} is empty."
    else
      echo "Branch diff against ${base_ref} is limited to the Evidence Court v0.1 release set."
    fi
  fi
  return "${invalid}"
}

verify_artifact_dir() {
  local artifact_dir="${1:-}"
  if [[ -z "${artifact_dir}" ]]; then
    echo "--verify-artifact-dir requires a directory" >&2
    return 2
  fi

  "${PY}" - "${artifact_dir}" <<'PY'
import hashlib
import json
import re
import sys
from pathlib import Path

artifact_dir = Path(sys.argv[1])

def fail(message: str) -> None:
    raise SystemExit(message)

def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)

def read_text(name: str) -> str:
    path = artifact_dir / name
    require(path.is_file(), f"missing artifact file: {name}")
    return path.read_text(encoding="utf-8")

require(artifact_dir.is_dir(), f"artifact dir not found: {artifact_dir}")
manifest_path = artifact_dir / "artifact-manifest.json"
require(manifest_path.is_file(), "missing artifact file: artifact-manifest.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

expected_review_path = [
    "reviewer-quickstart.md",
    "bad-run.md",
    "redacted-real-world-bad-run.json",
    "fail-on-fail.json",
    "good-run.json",
    "marked-transcript.json",
    "openmako-agent-run-result.json",
    "jsonl-events.json",
    "mixed-source-rejection.txt",
    "smoke-summary.txt",
]
expected_files = {"artifact-manifest.json", *expected_review_path}
actual_files = {path.name for path in artifact_dir.iterdir() if path.is_file()}
require(actual_files == expected_files, f"artifact file set mismatch: {sorted(actual_files)}")
require(manifest.get("artifact") == "evidence-court-smoke", "artifact manifest has wrong artifact name")
require(manifest.get("version") == "v0.1", "artifact manifest has wrong version")
require("supplied JSON run records" in manifest.get("safe_claim", ""), "artifact manifest missing safe claim")
require("OpenMako AgentRunResult JSON producer artifacts" in manifest.get("safe_claim", ""), "artifact manifest missing AgentRunResult safe claim")
require(manifest.get("review_path") == expected_review_path, "artifact manifest review_path mismatch")

hashes = manifest.get("artifact_file_sha256")
require(isinstance(hashes, dict), "artifact manifest missing artifact_file_sha256")
require(set(hashes) == set(expected_review_path), "artifact hash keys do not match review_path")
for name in expected_review_path:
    digest = hashes[name]
    require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, f"invalid artifact SHA-256: {name}")
    actual = hashlib.sha256((artifact_dir / name).read_bytes()).hexdigest()
    require(actual == digest, f"artifact SHA-256 mismatch: {name}")

expected_checks = manifest.get("expected_checks", {})
require(expected_checks.get("bad-run.md") == "## Verdict: FAIL", "manifest missing bad-run expected check")
require(expected_checks.get("redacted-real-world-bad-run.json") == '"verdict": "FAIL"', "manifest missing redacted expected check")
require(
    expected_checks.get("fail-on-fail.json") == '"verdict": "FAIL" and command exit code 1',
    "manifest missing fail-on-fail expected check",
)
require(expected_checks.get("good-run.json") == '"verdict": "PASS"', "manifest missing good-run expected check")
require(expected_checks.get("openmako-agent-run-result.json") == '"verdict": "FAIL"', "manifest missing AgentRunResult expected check")
require(expected_checks.get("jsonl-events.json") == '"verdict": "FAIL"', "manifest missing JSONL expected check")

source_checks = manifest.get("source_provenance_checks", {})
require(source_checks.get("bad-run.md") == "source: bad-run-demo", "manifest missing bad-run source check")
require(
    source_checks.get("redacted-real-world-bad-run.json")
    == "source: examples/evidence-court/redacted-real-world-bad-run.json",
    "manifest missing redacted source check",
)
require(source_checks.get("fail-on-fail.json") == "source: bad-run-demo", "manifest missing fail-on source check")
require(source_checks.get("good-run.json") == "source: good-run-demo", "manifest missing good-run source check")
require(
    source_checks.get("marked-transcript.json") == "source: tests/fixtures/evidence_court/marked_bad_transcript.txt",
    "manifest missing transcript source check",
)
require(
    source_checks.get("openmako-agent-run-result.json")
    == "source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
    "manifest missing AgentRunResult source check",
)
require(source_checks.get("jsonl-events.json") == "source: ", "manifest missing JSONL source check")

ci_policy_recipe = manifest.get("ci_policy_recipe", {})
require(
    ci_policy_recipe.get("required_test_gate")
    == "mako evidence-court --input <run-record.json> --fail-on-reason-code test.required_not_run --json",
    "manifest missing required-test CI policy recipe",
)
require(
    ci_policy_recipe.get("effect")
    == "exits 1 when the supplied record omits the required test command",
    "manifest missing CI policy recipe effect",
)

boundaries = set(manifest.get("boundaries", []))
require("No native Claude/Codex/Cursor/Devin/CI log ingestion claim." in boundaries, "manifest missing native-ingestion boundary")
require("No proof that tests ran outside the supplied record." in boundaries, "manifest missing supplied-record boundary")
require("No broad SWE repair, unknown NPM reasoning, or Desktop L4/L5 autonomy claim." in boundaries, "manifest missing autonomy boundary")

content_checks = {
    "reviewer-quickstart.md": [
        "## 30-Second Review Path",
        "Open `bad-run.md` first",
        "Open `redacted-real-world-bad-run.json`",
        "artifact file SHA-256 hashes",
        "## CI Policy Recipe",
        "--fail-on-reason-code test.required_not_run",
        "does not rerun tests or parse native CI logs",
        "does not prove native Claude/Codex/Cursor/Devin/CI log ingestion",
    ],
    "bad-run.md": [
        "## Verdict: FAIL",
        "source: bad-run-demo",
        "edited protected path: tests/test_calculator.py",
        "required test not run: python -m pytest tests/test_calculator.py -q",
    ],
    "redacted-real-world-bad-run.json": [
        '"verdict": "FAIL"',
        "source: examples/evidence-court/redacted-real-world-bad-run.json",
        "edited protected path: tests/test_api_guard.py",
        "edited protected path: .github/workflows/ci.yml",
        "required test not run: python -m pytest tests/test_api_guard.py -q",
    ],
    "fail-on-fail.json": ['"verdict": "FAIL"', "source: bad-run-demo"],
    "good-run.json": ['"verdict": "PASS"', "source: good-run-demo"],
    "marked-transcript.json": [
        '"verdict": "FAIL"',
        "source: tests/fixtures/evidence_court/marked_bad_transcript.txt",
    ],
    "openmako-agent-run-result.json": [
        '"verdict": "FAIL"',
        "source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
        "edited protected path: tests/test_calculator.py",
        "required test not run: python -m pytest tests/test_calculator.py -q",
    ],
    "jsonl-events.json": [
        '"verdict": "FAIL"',
        "required test not run: python -m pytest tests/test_calculator.py -q",
    ],
    "mixed-source-rejection.txt": ["exit_code=2"],
    "smoke-summary.txt": [
        "Evidence Court smoke gate passed.",
        "reason-code gate checked bad-run exits 1 with --fail-on-reason-code test.required_not_run.",
        "review-path artifacts must have SHA-256 hashes",
    ],
}
for name, needles in content_checks.items():
    text = read_text(name)
    for needle in needles:
        require(needle in text, f"artifact content missing in {name}: {needle}")

print(f"Evidence Court artifact dir verified: {artifact_dir}")
PY
}

mode="${1:---check}"
case "${mode}" in
  --list)
    list_paths
    ;;
  --check)
    check_paths_exist
    check_staged_files
    ;;
  --check-staged-release-set)
    check_paths_exist
    check_staged_release_set
    ;;
  --audit-staged-claim-copy)
    check_paths_exist
    check_staged_release_set
    audit_staged_claim_copy
    ;;
  --check-branch-diff)
    check_paths_exist
    check_branch_diff "${2:-${EVIDENCE_COURT_BASE_REF:-main}}"
    ;;
  --verify-artifact-dir)
    verify_artifact_dir "${2:-}"
    ;;
  -h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
