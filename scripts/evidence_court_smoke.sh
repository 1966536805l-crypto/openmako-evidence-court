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

run_package_install_smoke() {
  local smoke_root
  local src_dir
  local dist_dir
  local build_log
  local venv_dir
  smoke_root="$(mktemp -d "${TMPDIR:-/tmp}/openmako-package-smoke.XXXXXX")"
  src_dir="${smoke_root}/src"
  dist_dir="${smoke_root}/dist"
  build_log="${smoke_root}/build.log"
  venv_dir="${smoke_root}/venv"
  mkdir -p "${dist_dir}" "${src_dir}/examples/evidence-court" "${src_dir}/docs"
  cp setup.py pyproject.toml MANIFEST.in LICENSE "${src_dir}/"
  cp docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md "${src_dir}/docs/"
  cp docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md "${src_dir}/README.md"
  cp -R quantagent "${src_dir}/"
  cp examples/evidence-court/bad-run.json examples/evidence-court/good-run.json "${src_dir}/examples/evidence-court/"

  (
    cd "${src_dir}"
    "${PY}" setup.py sdist --dist-dir "${dist_dir}" bdist_wheel --dist-dir "${dist_dir}"
  ) > "${build_log}" 2>&1
  if grep -Eqi "warning: (no files found|.*not found|file .*missing)" "${build_log}"; then
    echo "package build emitted missing-file warning" >&2
    cat "${build_log}" >&2
    rm -rf "${smoke_root}"
    exit 1
  fi

  "${PY}" - "${dist_dir}" <<'PY'
import configparser
import sys
import tarfile
import zipfile
from pathlib import Path

dist_dir = Path(sys.argv[1])
wheels = sorted(dist_dir.glob("open_mako-0.1.3-*.whl"))
if len(wheels) != 1:
    raise SystemExit(f"expected one open_mako 0.1.3 wheel, found {len(wheels)}")
sdists = sorted(dist_dir.glob("open_mako-0.1.3.tar.gz")) + sorted(dist_dir.glob("open-mako-0.1.3.tar.gz"))
if len(sdists) != 1:
    raise SystemExit("expected open_mako 0.1.3 sdist")

wheel = wheels[0]
with zipfile.ZipFile(wheel) as archive:
    names = set(archive.namelist())
    def require(condition: bool, message: str) -> None:
        if not condition:
            raise SystemExit(message)

    expected_quantagent_modules = {
        "quantagent/__init__.py",
        "quantagent/evidence_court.py",
    }
    quantagent_modules = {
        name for name in names if name.startswith("quantagent/") and name.endswith(".py")
    }
    require(
        quantagent_modules == expected_quantagent_modules,
        f"wheel quantagent module boundary changed: {sorted(quantagent_modules)}",
    )
    require("quantagent/__init__.py" in names, "wheel missing quantagent/__init__.py")
    require("quantagent/evidence_court.py" in names, "wheel missing quantagent/evidence_court.py")
    require("quantagent/cli.py" not in names, "wheel must not include quantagent/cli.py")
    require("quantagent/vendor/__init__.py" not in names, "wheel must not include quantagent/vendor")
    require(
        any(name.endswith("share/open-mako/examples/evidence-court/bad-run.json") for name in names),
        "wheel missing bad-run example",
    )
    require(
        any(name.endswith("share/open-mako/examples/evidence-court/good-run.json") for name in names),
        "wheel missing good-run example",
    )
    require(
        any(name.endswith(".dist-info/LICENSE") or name.endswith(".dist-info/licenses/LICENSE") for name in names),
        "wheel missing LICENSE file",
    )
    metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
    metadata = archive.read(metadata_name).decode("utf-8")
    require("OpenMako Evidence Court" in metadata, "wheel metadata missing Evidence Court readme")
    require("License: MIT" in metadata, "wheel metadata missing MIT license")
    require("License-File: LICENSE" in metadata, "wheel metadata missing License-File")
    require("Extreme Planner" not in metadata, "wheel metadata must not include broad planner claims")
    require("mako quant" not in metadata, "wheel metadata must not include broad quant commands")
    require("Agent Failure Autopsy" not in metadata, "wheel metadata must not include broad runtime claims")
    require("OpenClaw-style personal assistant" not in metadata, "wheel metadata must not include broad assistant claims")
    require("docs/LAUNCH_PLAYBOOK.md" not in metadata, "wheel metadata must not include stale launch-playbook links")
    require("Version: 0.1.3" in metadata, "wheel metadata version mismatch")
    entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
    parser = configparser.ConfigParser()
    parser.read_string(archive.read(entry_points_name).decode("utf-8"))
    scripts = parser["console_scripts"]
    for script in ("mako", "openmako", "qagent"):
        require(scripts.get(script) == "quantagent.evidence_court:main", f"bad console script: {script}")

sdist = sdists[0]
with tarfile.open(sdist) as archive:
    names = set(archive.getnames())
    def has_suffix(suffix: str) -> bool:
        return any(name.endswith(suffix) for name in names)

    quantagent_modules = sorted(
        name.rsplit("/", 2)[-2:]
        for name in names
        if "/quantagent/" in name and name.endswith(".py")
    )
    require(
        quantagent_modules == [["quantagent", "__init__.py"], ["quantagent", "evidence_court.py"]],
        f"sdist quantagent module boundary changed: {quantagent_modules}",
    )
    require(has_suffix("/quantagent/__init__.py"), "sdist missing quantagent/__init__.py")
    require(has_suffix("/quantagent/evidence_court.py"), "sdist missing quantagent/evidence_court.py")
    require(has_suffix("/LICENSE"), "sdist missing LICENSE")
    require(has_suffix("/docs/EVIDENCE_COURT_V0_1_PACKAGE_README.md"), "sdist missing package README")
    require(not has_suffix("/quantagent/cli.py"), "sdist must not include quantagent/cli.py")
    require(not any("/quantagent/vendor/" in name for name in names), "sdist must not include quantagent/vendor")

print(wheel)
PY

  local wheel_path
  wheel_path="$(ls "${dist_dir}"/open_mako-0.1.3-*.whl)"
  "${PY}" -m venv "${venv_dir}"
  PYTHONPATH= "${venv_dir}/bin/python" -m pip install --force-reinstall --no-index "${wheel_path}" > "${smoke_root}/install.log" 2>&1
  PYTHONPATH= "${PY}" - "${venv_dir}/bin" <<'PY'
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

bin_dir = Path(sys.argv[1])
child_env = os.environ.copy()
for key in ("GIT_INDEX_FILE", "PYTHONPATH", "PYTHONPYCACHEPREFIX"):
    child_env.pop(key, None)
child_env["PYTHONDONTWRITEBYTECODE"] = "1"
version_proc = subprocess.run(
    [str(bin_dir / "python"), "-c", "import quantagent; print(quantagent.__version__)"],
    cwd=str(bin_dir.parent),
    env=child_env,
    text=True,
    capture_output=True,
    timeout=30,
)
if version_proc.returncode != 0:
    raise SystemExit(f"installed package version probe failed: {version_proc.stderr}{version_proc.stdout}")
if version_proc.stdout.strip() != "0.1.3":
    raise SystemExit(f"installed package __version__ mismatch: {version_proc.stdout.strip()}")
checks = [
    ("mako", "bad-run", "FAIL"),
    ("openmako", "good-run", "PASS"),
    ("qagent", "good-run", "PASS"),
]
direct_console = (
    os.environ.get("EVIDENCE_COURT_DIRECT_CONSOLE_SMOKE") == "1"
    or (os.environ.get("EVIDENCE_COURT_DIRECT_CONSOLE_SMOKE") != "0" and platform.system() != "Darwin")
)
for script, demo, expected in checks:
    script_path = bin_dir / script
    if not script_path.is_file():
        raise SystemExit(f"missing installed console script: {script}")
    script_text = script_path.read_text(encoding="utf-8")
    if "from quantagent.evidence_court import main" not in script_text:
        raise SystemExit(f"installed console script does not import Evidence Court: {script}")
    command = [str(script_path), "evidence-court", "--demo", demo, "--json"]
    if not direct_console:
        command = [str(bin_dir / "python"), *command]
    proc = subprocess.run(
        command,
        cwd=str(bin_dir.parent),
        env=child_env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise SystemExit(f"{script} exited {proc.returncode}: {proc.stderr}{proc.stdout}")
    payload = json.loads(proc.stdout)
    if payload.get("verdict") != expected:
        raise SystemExit(f"{script} expected {expected}, got {payload.get('verdict')}")
print(f"package console smoke mode: {'direct' if direct_console else 'python-wrapper'}")
PY
  rm -rf "${smoke_root}"
}

if [[ -n "${ARTIFACT_DIR}" ]]; then
  mkdir -p "${ARTIFACT_DIR}"
fi

echo "[evidence-court-smoke] compile"
"${PY}" -m py_compile quantagent/evidence_court.py tests/test_evidence_court.py

echo "[evidence-court-smoke] focused tests"
"${PY}" -m pytest -p no:cacheprovider tests/test_evidence_court.py -q

echo "[evidence-court-smoke] bad demo must fail"
bad_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --demo bad-run)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${bad_output}" > "${ARTIFACT_DIR}/bad-run.md"
fi
grep -q "## Verdict: FAIL" <<< "${bad_output}"

echo "[evidence-court-smoke] fail-on gate must block fail verdicts"
set +e
fail_on_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --demo bad-run --fail-on fail --json 2>&1)"
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

echo "[evidence-court-smoke] good demo must pass"
good_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --demo good-run --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${good_output}" > "${ARTIFACT_DIR}/good-run.json"
fi
grep -q '"verdict": "PASS"' <<< "${good_output}"

echo "[evidence-court-smoke] marked transcript must fail closed"
transcript_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${transcript_output}" > "${ARTIFACT_DIR}/marked-transcript.json"
fi
grep -q '"verdict": "FAIL"' <<< "${transcript_output}"

jsonl_events_file="$(mktemp "${TMPDIR:-/tmp}/evidence-court-events.XXXXXX")"
cat > "${jsonl_events_file}" <<'JSONL'
{"event":"claimed_task","text":"Fix calculator.add; only calculator.py may be edited."}
{"event":"final_claim","text":"Done. The calculator bug is fixed and tests pass."}
{"event":"file_read","path":"calculator.py"}
{"event":"file_edit","path":"tests/test_calculator.py"}
{"event":"command","command":"python -m py_compile calculator.py"}
{"event":"required_test","command":"python -m pytest tests/test_calculator.py -q"}
JSONL

echo "[evidence-court-smoke] explicit JSONL events must fail closed"
jsonl_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --from-jsonl-events "${jsonl_events_file}" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${jsonl_output}" > "${ARTIFACT_DIR}/jsonl-events.json"
fi
grep -q '"verdict": "FAIL"' <<< "${jsonl_output}"
grep -q '"required test not run: python -m pytest tests/test_calculator.py -q"' <<< "${jsonl_output}"

openmako_result_file="$(mktemp "${TMPDIR:-/tmp}/evidence-court-openmako-result.XXXXXX")"
"${PY}" - "${openmako_result_file}" <<'PY'
import json
import sys
from pathlib import Path

output_path = Path(sys.argv[1])
payload = {
    "source": "openmako-agent-result-shaped-record",
    "task": "create hello.py with greet function and test it",
    "ok": False,
    "status": "failed",
    "summary": "Done. Tests pass.",
    "failure_class": "verification_failed",
    "final_mode": "build",
    "runtime_context": {},
    "route": {},
    "plan": [],
    "observations": [
        {
            "step": 1,
            "name": "implement",
            "kind": "tool",
            "ok": True,
            "summary": "wrote hello.py",
            "mode": "build",
            "data": {"files_touched": ["hello.py"], "created_files": ["hello.py"]},
        },
        {
            "step": 2,
            "name": "verification_required",
            "kind": "internal",
            "ok": False,
            "summary": "post-edit verification missing after file changes",
            "mode": "build",
            "data": {
                "files_touched": ["hello.py"],
                "required_verification": ["validate", "unit_tests"],
            },
        },
    ],
}
output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

echo "[evidence-court-smoke] OpenMako AgentRunResult-shaped record must fail closed"
openmako_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --input "${openmako_result_file}" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${openmako_output}" > "${ARTIFACT_DIR}/openmako-agent-result.json"
fi
grep -q '"verdict": "FAIL"' <<< "${openmako_output}"
grep -q '"required test not run: validate"' <<< "${openmako_output}"
grep -q '"required test not run: unit_tests"' <<< "${openmako_output}"
grep -q "source: openmako-agent-result-shaped-record" <<< "${openmako_output}"

ci_log_dir="${ARTIFACT_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/evidence-court-ci-log.XXXXXX")}"
github_actions_log="${ci_log_dir}/github-actions-test-step.log"
github_actions_job_log="${ci_log_dir}/github-actions-job-log.log"
failed_pytest_log="${ci_log_dir}/failed-pytest-log.log"
cat > "${github_actions_log}" <<'EOF'
2026-06-05T11:22:33.0000000Z ##[group]Run actions/setup-python@v5
2026-06-05T11:22:33.0000000Z ##[endgroup]
2026-06-05T11:22:34.0000000Z ##[group]Run python -m pytest tests/test_calculator.py -q
2026-06-05T11:22:34.0000000Z python -m pytest tests/test_calculator.py -q
2026-06-05T11:22:35.0000000Z .                                                                        [100%]
2026-06-05T11:22:35.0000000Z 1 passed in 0.02s
2026-06-05T11:22:35.0000000Z ##[endgroup]
EOF
cat > "${github_actions_job_log}" <<'EOF'
2026-06-05T11:21:00.0000000Z ##[group]Run actions/setup-python@v5
2026-06-05T11:21:01.0000000Z Python setup complete
2026-06-05T11:21:02.0000000Z ##[endgroup]
2026-06-05T11:22:00.0000000Z ##[group]Run python -m pytest tests/test_evidence_court.py \
2026-06-05T11:22:00.0000000Z   tests/test_evidence_court_smoke_script.py -q
2026-06-05T11:22:00.0000000Z shell: /usr/bin/bash -e {0}
2026-06-05T11:22:01.0000000Z python -m pytest tests/test_evidence_court.py \
2026-06-05T11:22:01.0000000Z   tests/test_evidence_court_smoke_script.py -q
2026-06-05T11:22:18.0000000Z 69 passed in 18.47s
2026-06-05T11:22:19.0000000Z ##[endgroup]
EOF
cat > "${failed_pytest_log}" <<'EOF'
$ python -m pytest tests/test_calculator.py -q
FAILED tests/test_calculator.py::test_add - AssertionError
1 failed in 0.03s
EOF

echo "[evidence-court-smoke] supplied GitHub Actions test-step log must pass"
github_actions_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --from-ci-log "${github_actions_log}" --claim "Fixed. Tests pass." --required-test "python -m pytest tests/test_calculator.py -q" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${github_actions_output}" > "${ARTIFACT_DIR}/github-actions-test-step.json"
fi
grep -q '"verdict": "PASS"' <<< "${github_actions_output}"
grep -q "github-actions-test-step.log" <<< "${github_actions_output}"
grep -q "test command observed: python -m pytest tests/test_calculator.py -q" <<< "${github_actions_output}"

echo "[evidence-court-smoke] supplied GitHub Actions job log must pass"
github_actions_job_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --from-ci-log "${github_actions_job_log}" --claim "Release tests pass." --required-test "python -m pytest tests/test_evidence_court.py tests/test_evidence_court_smoke_script.py -q" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${github_actions_job_output}" > "${ARTIFACT_DIR}/github-actions-job-log.json"
fi
grep -q '"verdict": "PASS"' <<< "${github_actions_job_output}"
grep -q "github-actions-job-log.log" <<< "${github_actions_job_output}"
grep -q "test command observed: python -m pytest tests/test_evidence_court.py tests/test_evidence_court_smoke_script.py -q" <<< "${github_actions_job_output}"

echo "[evidence-court-smoke] supplied failed pytest log must fail closed"
failed_pytest_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --from-ci-log "${failed_pytest_log}" --claim "Fixed. Tests pass." --required-test "python -m pytest tests/test_calculator.py -q" --json)"
if [[ -n "${ARTIFACT_DIR}" ]]; then
  printf '%s\n' "${failed_pytest_output}" > "${ARTIFACT_DIR}/failed-pytest-log.json"
fi
grep -q '"verdict": "FAIL"' <<< "${failed_pytest_output}"
grep -q "failed-pytest-log.log" <<< "${failed_pytest_output}"
grep -q "test output status: failed" <<< "${failed_pytest_output}"

echo "[evidence-court-smoke] mixed evidence sources must be rejected"
set +e
mixed_output="$("${PY}" -m quantagent.evidence_court --no-trust-prompt evidence-court --input examples/evidence-court/bad-run.json --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --from-jsonl-events "${jsonl_events_file}" 2>&1)"
mixed_code=$?
set -e
rm -f "${jsonl_events_file}" "${openmako_result_file}"
if [[ -z "${ARTIFACT_DIR}" ]]; then
  rm -rf "${ci_log_dir}"
fi
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
if [[ -n "${EVIDENCE_COURT_BRANCH_DIFF_BASE:-}" ]]; then
  bash scripts/evidence_court_release_set.sh --check-branch-diff "${EVIDENCE_COURT_BRANCH_DIFF_BASE}"
else
  bash scripts/evidence_court_release_set.sh --check
fi

echo "[evidence-court-smoke] package install smoke"
run_package_install_smoke

echo "[evidence-court-smoke] README boundary claim"
grep -q "does not yet natively ingest Claude Code, Codex, Cursor, or Devin logs" README.md
grep -q "The CI-log path is intentionally narrower" README.md
grep -q "not arbitrary CI ingestion" README.md
grep -q "Claim: Done. The calculator bug is fixed and tests pass." README.md
grep -q "Evidence: required test not run: python -m pytest tests/test_calculator.py -q" README.md

if [[ -n "${ARTIFACT_DIR}" ]]; then
  cat > "${ARTIFACT_DIR}/artifact-manifest.json" <<'EOF'
{
  "artifact": "evidence-court-smoke",
  "version": "v0.1",
  "safe_claim": "Evidence Court audits supplied JSON run records, explicit marked transcript v0 files, and explicit Evidence Court JSONL event streams for claim/evidence/scope/test mismatches.",
  "review_path": [
    "reviewer-quickstart.md",
    "bad-run.md",
    "fail-on-fail.json",
    "good-run.json",
    "marked-transcript.json",
    "jsonl-events.json",
    "openmako-agent-result.json",
    "github-actions-test-step.log",
    "github-actions-test-step.json",
    "github-actions-job-log.log",
    "github-actions-job-log.json",
    "failed-pytest-log.log",
    "failed-pytest-log.json",
    "mixed-source-rejection.txt",
    "smoke-summary.txt"
  ],
  "expected_checks": {
    "bad-run.md": "## Verdict: FAIL",
    "fail-on-fail.json": "\"verdict\": \"FAIL\" and command exit code 1",
    "good-run.json": "\"verdict\": \"PASS\"",
    "marked-transcript.json": "\"verdict\": \"FAIL\"",
    "jsonl-events.json": "\"verdict\": \"FAIL\"",
    "openmako-agent-result.json": "\"verdict\": \"FAIL\"",
    "github-actions-test-step.json": "\"verdict\": \"PASS\"",
    "github-actions-job-log.json": "\"verdict\": \"PASS\"",
    "failed-pytest-log.json": "\"verdict\": \"FAIL\"",
    "mixed-source-rejection.txt": "exit_code=2",
    "smoke-summary.txt": "Evidence Court smoke gate passed."
  },
  "source_provenance_checks": {
    "bad-run.md": "source: bad-run-demo",
    "fail-on-fail.json": "source: bad-run-demo",
    "good-run.json": "source: good-run-demo",
    "marked-transcript.json": "source: tests/fixtures/evidence_court/marked_bad_transcript.txt",
    "jsonl-events.json": "source: ",
    "openmako-agent-result.json": "source: openmako-agent-result-shaped-record",
    "github-actions-test-step.json": "github-actions-test-step.log",
    "github-actions-job-log.json": "github-actions-job-log.log",
    "failed-pytest-log.json": "failed-pytest-log.log"
  },
  "boundaries": [
    "No native Claude/Codex/Cursor/Devin transcript ingestion claim.",
    "The CI-log path only audits supplied pytest logs, GitHub Actions test-step logs, or GitHub Actions job logs with visible supported test commands.",
    "No proof that tests ran outside the supplied record or supplied log.",
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
3. Open `fail-on-fail.json`: the same bad run is executed with `--fail-on fail`, and the smoke gate only writes this artifact after the command exits with code 1.
4. Open `good-run.json`: the supplied run record stays in scope, reports the required pytest command, returns `"verdict": "PASS"`, and includes `source: good-run-demo`.
5. Open `marked-transcript.json`: explicit marked transcript v0 input returns `"verdict": "FAIL"` and includes the fixture path as `source`.
6. Open `jsonl-events.json`: explicit Evidence Court JSONL event stream input returns `"verdict": "FAIL"` and includes the generated JSONL path as `source`.
7. Open `openmako-agent-result.json`: an OpenMako AgentRunResult-shaped producer record returns `"verdict": "FAIL"` when the record reports `verification_required` but no test command.
8. Open `github-actions-test-step.log`, then `github-actions-test-step.json`: a supplied GitHub Actions pytest test-step log with a visible supported test command returns `"verdict": "PASS"`.
9. Open `github-actions-job-log.log`, then `github-actions-job-log.json`: a supplied full GitHub Actions job log with a visible supported pytest step returns `"verdict": "PASS"`.
10. Open `failed-pytest-log.log`, then `failed-pytest-log.json`: a supplied failed pytest log returns `"verdict": "FAIL"`.
11. Open `mixed-source-rejection.txt`: mixed JSON plus transcript plus JSONL inputs fail closed with `exit_code=2`.
12. Open `smoke-summary.txt`: the smoke gate reports `Evidence Court smoke gate passed.`

This artifact shows these fixtures: `bad-run` fails, `good-run` passes, marked transcript v0 input fails closed, explicit JSONL event input fails closed, OpenMako AgentRunResult-shaped input fails closed, supplied GitHub Actions pytest test-step log input passes, supplied full GitHub Actions job log input passes, supplied failed pytest log input fails closed, and mixed input modes are rejected.

## Boundary

This artifact shows the smoke gate output for supplied JSON, marked transcript v0, explicit Evidence Court JSONL event records, supplied pytest/GitHub Actions test-step logs, and supplied GitHub Actions job logs with visible supported test commands. It does not prove native Claude/Codex/Cursor/Devin transcript ingestion, arbitrary CI ingestion, or that tests really ran outside the supplied record/log.

It does not prove broad SWE repair, unknown NPM reasoning, or Desktop L4/L5 autonomy.

Safe claim: Evidence Court v0.1 audits supplied JSON run records, explicit marked transcript v0 files, explicit Evidence Court JSONL event streams, supplied pytest/GitHub Actions test-step logs, and supplied GitHub Actions job logs for claim/evidence/scope/test mismatches.
EOF
  cat > "${ARTIFACT_DIR}/smoke-summary.txt" <<'EOF'
Evidence Court smoke gate passed.
artifact-manifest.json lists the safe claim and expected review checks.
artifact-manifest.json lists source provenance checks for every generated report.
artifact-manifest.json lists SHA-256 hashes for every file in the review path.
reviewer-quickstart.md gives the 30-second review path.
compile gate passed for quantagent/evidence_court.py and focused tests.
focused tests passed for tests/test_evidence_court.py.
demo verdict gate checked bad-run FAIL and good-run PASS.
fail-on gate checked bad-run exits 1 with --fail-on fail.
input-mode gate checked marked transcript FAIL, explicit JSONL events FAIL, and mixed JSON plus transcript plus JSONL rejection.
OpenMako AgentRunResult-shaped record gate checked verification_required and no test command returns FAIL.
CI-log gate checked a supplied GitHub Actions pytest test-step log returns PASS, a supplied full GitHub Actions job log returns PASS, and a supplied failed pytest log returns FAIL.
release boundary gate checked the Evidence Court release set.
package install smoke checked open-mako 0.1.3 wheel contents, metadata boundary, package version, and mako/openmako/qagent console aliases.
bad-run.md must contain Verdict: FAIL.
fail-on-fail.json must contain "verdict": "FAIL" and is only written after exit code 1.
good-run.json must contain "verdict": "PASS".
marked-transcript.json must contain "verdict": "FAIL".
jsonl-events.json must contain "verdict": "FAIL".
openmako-agent-result.json must contain "verdict": "FAIL".
github-actions-test-step.json must contain "verdict": "PASS".
github-actions-job-log.json must contain "verdict": "PASS".
failed-pytest-log.json must contain "verdict": "FAIL".
report artifacts must contain source provenance in their Evidence section.
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
