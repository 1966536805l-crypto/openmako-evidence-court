from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


class EvidenceCourtSmokeScriptTest(unittest.TestCase):
    def _run_release_set_with_staged_paths(
        self,
        root: Path,
        *paths: str,
        mode: str = "--check",
    ) -> subprocess.CompletedProcess[str]:
        script = root / "scripts" / "evidence_court_release_set.sh"
        env = os.environ.copy()
        with tempfile.TemporaryDirectory(prefix="openmako-release-index-") as tmp:
            env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
            read_tree = subprocess.run(
                ["git", "read-tree", "HEAD"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(read_tree.returncode, 0, read_tree.stdout + read_tree.stderr)
            for path in paths:
                source = root / path
                content = source.read_text(encoding="utf-8") if source.exists() else ""
                self._stage_synthetic_blob(root, env, path, content + "\n")
            return subprocess.run(
                ["bash", str(script), mode],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )

    def _stage_synthetic_blob(self, root: Path, env: dict[str, str], path: str, content: str) -> None:
        blob = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=root,
            env=env,
            input=content,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(blob.returncode, 0, blob.stdout + blob.stderr)
        update = subprocess.run(
            ["git", "update-index", "--add", "--cacheinfo", "100644", blob.stdout.strip(), path],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(update.returncode, 0, update.stdout + update.stderr)

    def _assert_not_self_hosted_third_party_evidence_url(self, url_cell: str) -> None:
        url = url_cell.strip().strip("`")
        parsed = urlparse(url)
        self.assertNotEqual(
            (parsed.netloc, parsed.path.rstrip("/")),
            ("github.com", "/1966536805l-crypto/openmako-evidence-court"),
        )
        self.assertFalse(
            parsed.netloc == "github.com"
            and parsed.path.startswith("/1966536805l-crypto/openmako-evidence-court/"),
            msg=f"self-hosted repo URL cannot prove third-party outreach: {url}",
        )

    def test_evidence_court_cli_runs_without_full_agent_runtime(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="openmako-evidence-cli-minimal-") as tmp:
            tmp_root = Path(tmp)
            package = tmp_root / "quantagent"
            package.mkdir()
            for name in ("__init__.py", "cli.py", "evidence_court.py"):
                (package / name).write_text((root / "quantagent" / name).read_text(encoding="utf-8"), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "quantagent.cli", "--no-trust-prompt", "evidence-court", "--demo", "good-run", "--json"],
                cwd=tmp_root,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["verdict"], "PASS")

    def test_smoke_script_runs_release_gate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_smoke.sh"
        self.assertTrue(os.access(script, os.X_OK), f"{script} must be executable")
        env = os.environ.copy()
        env["PYTHON"] = sys.executable
        env["PYTHONPATH"] = str(root)
        with tempfile.TemporaryDirectory(prefix="openmako-smoke-pycache-") as pycache:
            env["PYTHONPYCACHEPREFIX"] = pycache
            proc = subprocess.run(
                ["bash", str(script)],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=60,
            )

        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, output)
        self.assertIn("Evidence Court smoke gate passed.", output)
        self.assertIn("[evidence-court-smoke] release set boundary", output)

    def test_smoke_script_uses_branch_diff_gate_when_base_is_set(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_smoke.sh"
        text = script.read_text(encoding="utf-8")

        self.assertIn("EVIDENCE_COURT_BRANCH_DIFF_BASE", text)
        self.assertIn("--check-branch-diff", text)
        self.assertIn("--check", text)
        self.assertIn('! "${EVIDENCE_COURT_BRANCH_DIFF_BASE}" =~ ^0+$', text)
        self.assertIn("--artifact-dir DIR", text)
        self.assertIn("EVIDENCE_COURT_ARTIFACT_DIR provides the same setting for CI.", text)

    def test_smoke_script_rejects_unknown_arguments(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_smoke.sh"
        proc = subprocess.run(
            ["bash", str(script), "--unexpected"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=10,
        )

        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 2, output)
        self.assertIn("unknown argument for Evidence Court smoke gate: --unexpected", output)
        self.assertIn("--artifact-dir DIR writes reviewer-facing smoke artifacts", output)

    def test_smoke_script_writes_review_artifacts_when_requested(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_smoke.sh"
        env = os.environ.copy()
        env["PYTHON"] = sys.executable
        env["PYTHONPATH"] = str(root)
        with tempfile.TemporaryDirectory(prefix="openmako-smoke-artifacts-") as artifacts:
            with tempfile.TemporaryDirectory(prefix="openmako-smoke-pycache-") as pycache:
                env["PYTHONPYCACHEPREFIX"] = pycache
                proc = subprocess.run(
                    ["bash", str(script), "--artifact-dir", artifacts],
                    cwd=root,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=60,
                )

            output = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, output)
            artifact_root = Path(artifacts)
            expected = {
                "artifact-manifest.json",
                "bad-run.md",
                "fail-on-fail.json",
                "good-run.json",
                "jsonl-events.json",
                "marked-transcript.json",
                "mixed-source-rejection.txt",
                "openmako-agent-run-result.json",
                "redacted-real-world-bad-run.json",
                "reviewer-quickstart.md",
                "smoke-summary.txt",
            }
            self.assertEqual(expected, {path.name for path in artifact_root.iterdir()})
            manifest = json.loads((artifact_root / "artifact-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["artifact"], "evidence-court-smoke")
            self.assertEqual(manifest["version"], "v0.1")
            self.assertIn("safe_claim", manifest)
            self.assertIn("supplied JSON run records", manifest["safe_claim"])
            self.assertIn("OpenMako AgentRunResult JSON producer artifacts", manifest["safe_claim"])
            self.assertIn("explicit marked transcript v0 files", manifest["safe_claim"])
            self.assertIn("explicit Evidence Court JSONL event streams", manifest["safe_claim"])
            self.assertEqual(
                [
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
                ],
                manifest["review_path"],
            )
            self.assertEqual("## Verdict: FAIL", manifest["expected_checks"]["bad-run.md"])
            self.assertEqual('"verdict": "FAIL"', manifest["expected_checks"]["redacted-real-world-bad-run.json"])
            self.assertEqual('"verdict": "FAIL" and command exit code 1', manifest["expected_checks"]["fail-on-fail.json"])
            self.assertEqual('"verdict": "PASS"', manifest["expected_checks"]["good-run.json"])
            self.assertEqual('"verdict": "FAIL"', manifest["expected_checks"]["openmako-agent-run-result.json"])
            self.assertEqual('"verdict": "FAIL"', manifest["expected_checks"]["jsonl-events.json"])
            self.assertEqual("source: bad-run-demo", manifest["source_provenance_checks"]["bad-run.md"])
            self.assertEqual(
                "source: examples/evidence-court/redacted-real-world-bad-run.json",
                manifest["source_provenance_checks"]["redacted-real-world-bad-run.json"],
            )
            self.assertEqual("source: bad-run-demo", manifest["source_provenance_checks"]["fail-on-fail.json"])
            self.assertEqual("source: good-run-demo", manifest["source_provenance_checks"]["good-run.json"])
            self.assertEqual(
                "source: tests/fixtures/evidence_court/marked_bad_transcript.txt",
                manifest["source_provenance_checks"]["marked-transcript.json"],
            )
            self.assertEqual(
                "source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
                manifest["source_provenance_checks"]["openmako-agent-run-result.json"],
            )
            self.assertEqual("source: ", manifest["source_provenance_checks"]["jsonl-events.json"])
            self.assertEqual(
                "mako evidence-court --input <run-record.json> --fail-on-reason-code test.required_not_run --json",
                manifest["ci_policy_recipe"]["required_test_gate"],
            )
            self.assertEqual(
                "exits 1 when the supplied record omits the required test command",
                manifest["ci_policy_recipe"]["effect"],
            )
            self.assertEqual(set(manifest["review_path"]), set(manifest["artifact_file_sha256"]))
            for artifact_name, digest in manifest["artifact_file_sha256"].items():
                with self.subTest(artifact_name=artifact_name):
                    self.assertRegex(digest, r"^[0-9a-f]{64}$")
                    expected_digest = hashlib.sha256((artifact_root / artifact_name).read_bytes()).hexdigest()
                    self.assertEqual(expected_digest, digest)
            self.assertIn("No native Claude/Codex/Cursor/Devin/CI log ingestion claim.", manifest["boundaries"])
            quickstart = (artifact_root / "reviewer-quickstart.md").read_text(encoding="utf-8")
            self.assertIn("not another coding agent", quickstart)
            self.assertIn("claim-vs-evidence gate", quickstart)
            self.assertIn("## 30-Second Review Path", quickstart)
            self.assertIn("Open `artifact-manifest.json`", quickstart)
            self.assertIn("artifact file SHA-256 hashes", quickstart)
            self.assertIn("Open `bad-run.md` first", quickstart)
            self.assertIn("Confirm it includes `source: bad-run-demo`", quickstart)
            self.assertIn("Open `redacted-real-world-bad-run.json`", quickstart)
            self.assertIn("redacted supplied record returns", quickstart)
            self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", quickstart)
            self.assertIn("Open `fail-on-fail.json`", quickstart)
            self.assertIn("exits with code 1", quickstart)
            self.assertIn("supplied run record", quickstart)
            self.assertIn("Open `marked-transcript.json`", quickstart)
            self.assertIn("fixture path as `source`", quickstart)
            self.assertIn("Open `openmako-agent-run-result.json`", quickstart)
            self.assertIn("explicit OpenMako AgentRunResult input returns", quickstart)
            self.assertIn("Open `jsonl-events.json`", quickstart)
            self.assertIn("generated JSONL path as `source`", quickstart)
            self.assertIn("explicit Evidence Court JSONL event stream input returns", quickstart)
            self.assertIn("mixed JSON plus transcript plus JSONL inputs fail closed with `exit_code=2`", quickstart)
            self.assertIn("Open `smoke-summary.txt`", quickstart)
            self.assertIn("This artifact shows these fixtures", quickstart)
            self.assertIn("redacted supplied-record bad run fails", quickstart)
            self.assertIn("OpenMako AgentRunResult input fails closed", quickstart)
            self.assertIn("explicit JSONL event input fails closed", quickstart)
            self.assertIn("mixed input modes are rejected", quickstart)
            self.assertIn("## CI Policy Recipe", quickstart)
            self.assertIn("--fail-on-reason-code test.required_not_run", quickstart)
            self.assertIn("does not rerun tests or parse native CI logs", quickstart)
            self.assertIn("## Boundary", quickstart)
            self.assertIn("This artifact shows the smoke gate output", quickstart)
            self.assertNotIn("This artifact proves the smoke gate ran", quickstart)
            self.assertIn("OpenMako AgentRunResult producer artifacts", quickstart)
            self.assertIn("explicit Evidence Court JSONL event records", quickstart)
            self.assertIn("does not prove native Claude/Codex/Cursor/Devin/CI log ingestion", quickstart)
            self.assertIn("does not prove tests really ran outside the supplied record", quickstart)
            self.assertIn("does not prove broad SWE repair", quickstart)
            self.assertIn("Safe claim: Evidence Court v0.1 audits supplied JSON run records", quickstart)
            self.assertIn("OpenMako AgentRunResult JSON producer artifacts", quickstart)
            self.assertIn("explicit Evidence Court JSONL event streams", quickstart)
            self.assertIn("## Verdict: FAIL", (artifact_root / "bad-run.md").read_text(encoding="utf-8"))
            fail_on_json = (artifact_root / "fail-on-fail.json").read_text(encoding="utf-8")
            good_json = (artifact_root / "good-run.json").read_text(encoding="utf-8")
            marked_json = (artifact_root / "marked-transcript.json").read_text(encoding="utf-8")
            agent_run_result_json = (artifact_root / "openmako-agent-run-result.json").read_text(encoding="utf-8")
            jsonl_json = (artifact_root / "jsonl-events.json").read_text(encoding="utf-8")
            redacted_json = (artifact_root / "redacted-real-world-bad-run.json").read_text(encoding="utf-8")
            for report_json in (fail_on_json, good_json, marked_json, agent_run_result_json, jsonl_json, redacted_json):
                self.assertIn('"schema_version": "evidence-court.report.v0.1"', report_json)
            self.assertIn('"verdict": "FAIL"', redacted_json)
            self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", redacted_json)
            self.assertIn("edited protected path: tests/test_api_guard.py", redacted_json)
            self.assertIn("edited protected path: .github/workflows/ci.yml", redacted_json)
            self.assertIn("required test not run: python -m pytest tests/test_api_guard.py -q", redacted_json)
            self.assertIn('"verdict": "FAIL"', fail_on_json)
            self.assertIn("source: bad-run-demo", fail_on_json)
            self.assertIn('"verdict": "PASS"', good_json)
            self.assertIn("source: good-run-demo", good_json)
            self.assertIn('"verdict": "FAIL"', marked_json)
            self.assertIn("source: tests/fixtures/evidence_court/marked_bad_transcript.txt", marked_json)
            self.assertIn('"verdict": "FAIL"', agent_run_result_json)
            self.assertIn("source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json", agent_run_result_json)
            self.assertIn("edited protected path: tests/test_calculator.py", agent_run_result_json)
            self.assertIn(
                "required test not run: python -m pytest tests/test_calculator.py -q",
                agent_run_result_json,
            )
            self.assertIn('"verdict": "FAIL"', jsonl_json)
            self.assertIn("source: ", jsonl_json)
            self.assertIn(
                "required test not run: python -m pytest tests/test_calculator.py -q",
                jsonl_json,
            )
            self.assertIn("exit_code=2", (artifact_root / "mixed-source-rejection.txt").read_text(encoding="utf-8"))
            self.assertIn("Evidence Court smoke gate passed.", (artifact_root / "smoke-summary.txt").read_text(encoding="utf-8"))
            summary = (artifact_root / "smoke-summary.txt").read_text(encoding="utf-8")
            self.assertIn("artifact-manifest.json lists the safe claim", summary)
            self.assertIn("artifact-manifest.json lists source provenance checks", summary)
            self.assertIn("artifact-manifest.json lists SHA-256 hashes", summary)
            self.assertIn("reviewer-quickstart.md gives the 30-second review path.", summary)
            self.assertIn("compile gate passed", summary)
            self.assertIn("focused tests passed", summary)
            self.assertIn("demo verdict gate checked bad-run FAIL and good-run PASS", summary)
            self.assertIn("redacted supplied-record gate checked redacted-real-world-bad-run FAIL.", summary)
            self.assertIn("fail-on gate checked bad-run exits 1 with --fail-on fail.", summary)
            self.assertIn(
                "reason-code gate checked bad-run exits 1 with --fail-on-reason-code test.required_not_run.",
                summary,
            )
            self.assertIn("input-mode gate checked marked transcript FAIL, OpenMako AgentRunResult FAIL", summary)
            self.assertIn("explicit JSONL events FAIL", summary)
            self.assertIn("release boundary gate checked the Evidence Court release set", summary)
            self.assertIn("report artifacts must contain source provenance", summary)
            self.assertIn("review-path artifacts must have SHA-256 hashes", summary)
            verifier = subprocess.run(
                [
                    "bash",
                    str(root / "scripts" / "evidence_court_release_set.sh"),
                    "--verify-artifact-dir",
                    artifacts,
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(verifier.returncode, 0, verifier.stdout + verifier.stderr)
            self.assertIn("Evidence Court artifact dir verified:", verifier.stdout)

            (artifact_root / "bad-run.md").write_text("tampered\n", encoding="utf-8")
            tampered = subprocess.run(
                [
                    "bash",
                    str(root / "scripts" / "evidence_court_release_set.sh"),
                    "--verify-artifact-dir",
                    artifacts,
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertNotEqual(tampered.returncode, 0, tampered.stdout + tampered.stderr)
            self.assertIn("artifact SHA-256 mismatch: bad-run.md", tampered.stdout + tampered.stderr)

    def test_smoke_script_rejects_excluded_staged_release_file(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_smoke.sh"
        env = os.environ.copy()
        env["PYTHON"] = sys.executable
        env["PYTHONPATH"] = str(root)
        with tempfile.TemporaryDirectory(prefix="openmako-smoke-index-") as tmp:
            env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
            env["PYTHONPYCACHEPREFIX"] = str(Path(tmp) / "pycache")
            read_tree = subprocess.run(
                ["git", "read-tree", "HEAD"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(read_tree.returncode, 0, read_tree.stdout + read_tree.stderr)
            self._stage_synthetic_blob(
                root,
                env,
                "quantagent/agent_planner.py",
                "# synthetic excluded staged file for Evidence Court release-set test\n",
            )
            proc = subprocess.run(
                ["bash", str(script)],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=60,
            )

        output = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0, output)
        self.assertIn(
            "excluded file is staged for Evidence Court v0.1: quantagent/agent_planner.py",
            output,
        )

    def test_github_actions_workflow_runs_smoke_script(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = root / ".github" / "workflows" / "evidence-court.yml"

        text = workflow.read_text(encoding="utf-8")

        self.assertIn("Evidence Court Smoke", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn("actions/checkout@v6", text)
        self.assertIn("actions/setup-python@v6", text)
        self.assertIn("python -m pip install --upgrade pip pytest", text)
        self.assertIn("EVIDENCE_COURT_BRANCH_DIFF_BASE:", text)
        self.assertIn("github.event_name == 'pull_request'", text)
        self.assertIn("format('origin/{0}', github.base_ref)", text)
        self.assertIn("github.event.before", text)
        self.assertIn("EVIDENCE_COURT_ARTIFACT_DIR: evidence-court-artifacts", text)
        self.assertIn("run: bash scripts/evidence_court_smoke.sh", text)
        self.assertIn("Verify Evidence Court smoke artifacts", text)
        self.assertIn(
            "run: bash scripts/evidence_court_release_set.sh --verify-artifact-dir evidence-court-artifacts",
            text,
        )
        self.assertNotIn("EVIDENCE_COURT_BRANCH_DIFF_BASE=origin/main", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertNotIn("actions/checkout@v4", text)
        self.assertNotIn("actions/setup-python@v5", text)
        self.assertNotIn("actions/upload-artifact@v4", text)
        self.assertIn("name: evidence-court-smoke", text)
        self.assertIn("path: evidence-court-artifacts/", text)
        self.assertIn("if-no-files-found: error", text)
        self.assertRegex(
            text,
            re.compile(
                r"- name: Run Evidence Court smoke gate\s+env:\s+EVIDENCE_COURT_BRANCH_DIFF_BASE:[\s\S]*github\.event_name == 'pull_request'[\s\S]*github\.event\.before[\s\S]*EVIDENCE_COURT_ARTIFACT_DIR: evidence-court-artifacts\s+run: bash scripts/evidence_court_smoke\.sh",
                re.MULTILINE,
            ),
        )
        self.assertLess(
            text.index("Verify Evidence Court smoke artifacts"),
            text.index("Upload Evidence Court smoke artifacts"),
        )
        self.assertNotIn("pytest -p no:cacheprovider", text)

    def test_release_cut_checklist_separates_evidence_court_from_planner_work(self) -> None:
        root = Path(__file__).resolve().parents[1]
        checklist = root / "docs" / "EVIDENCE_COURT_V0_1_RELEASE_CUT.md"
        text = checklist.read_text(encoding="utf-8")
        included_paths = (
            ".github/ISSUE_TEMPLATE/technical-review-request.md",
            ".github/workflows/evidence-court.yml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "docs/CAPABILITY_GATES.md",
            "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md",
            "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
            "docs/EVIDENCE_COURT_COMPARISON.md",
            "docs/TECHNICAL_TREND_RADAR.md",
            "docs/REDACTION_GUIDE.md",
            "docs/CURRENT_PROOF_STATUS.md",
            "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md",
            "docs/EXPERT_REVIEW_BRIEF.md",
            "docs/OUTREACH.md",
            "docs/OUTREACH_TARGETS.md",
            "docs/TECHNICAL_REVIEW_REQUEST.md",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "docs/LAUNCH_POST.md",
            "docs/social-card.svg",
            "docs/RELEASE_NOTES_V0_1_0.md",
            "docs/RELEASE_NOTES_V0_1_1.md",
            "docs/RELEASE_NOTES_V0_1_2.md",
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/bad-run.report.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
            "quantagent/evidence_court.py",
            "quantagent/__init__.py",
            "quantagent/cli.py",
            "scripts/evidence_court_release_set.sh",
            "scripts/evidence_court_smoke.sh",
            "tests/fixtures/evidence_court/marked_bad_transcript.txt",
            "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
            "tests/fixtures/evidence_court/test_outputs/runner_outputs.json",
            "tests/test_evidence_court.py",
            "tests/test_evidence_court_smoke_script.py",
        )
        excluded_paths = (
            "quantagent/agent_planner.py",
            "tests/test_agent_planner_contract.py",
            "tests/test_external_benchmark_multimodule_regression.py",
        )

        for path in included_paths:
            with self.subTest(path=path):
                self.assertIn(f"`{path}`", text)
                self.assertTrue((root / path).exists())

        for path in excluded_paths:
            with self.subTest(path=path):
                self.assertIn(f"`{path}`", text)

        normalized = " ".join(text.split())
        self.assertIn("not a vendor log parser", normalized)
        self.assertIn("workflow wired locally", normalized)
        self.assertIn("machine-checkable file boundary", normalized)
        self.assertIn("bash scripts/evidence_court_smoke.sh", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-branch-diff main", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-staged-release-set", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy", text)
        self.assertIn(
            "python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q",
            text,
        )
        self.assertIn("git diff --check", text)
        self.assertIn("evidence-court-smoke", text)
        self.assertIn("artifact-manifest.json", text)
        self.assertIn("jsonl-events.json", text)
        self.assertIn("reviewer-quickstart.md", text)
        self.assertIn("smoke-summary.txt", text)
        self.assertIn("Artifact content check", text)
        self.assertIn("`artifact-manifest.json` lists the safe claim", text)
        self.assertIn("source provenance checks", text)
        self.assertIn("report artifacts include `source: ...`", text)
        self.assertIn("open `bad-run.md` first", text)
        self.assertIn("`bad-run.md` shows `Verdict: FAIL`", text)
        self.assertIn("`redacted-real-world-bad-run.json` contains `\"verdict\": \"FAIL\"`", text)
        self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", text)
        self.assertIn("`good-run.json` contains `\"verdict\": \"PASS\"`", text)
        self.assertIn("`jsonl-events.json` contains `\"verdict\": \"FAIL\"`", text)
        self.assertIn("`mixed-source-rejection.txt` contains `exit_code=2`", text)
        self.assertIn("green for the PR head commit", text)
        self.assertNotIn("After pushing the release branch", text)
        self.assertIn("Optional remote artifact download", text)
        self.assertIn(
            "gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn("sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json", text)

    def test_technical_trend_radar_keeps_external_project_boundaries(self) -> None:
        root = Path(__file__).resolve().parents[1]
        radar = root / "docs" / "TECHNICAL_TREND_RADAR.md"
        text = radar.read_text(encoding="utf-8")

        for project in (
            "Hermes Agent",
            "OpenClaw",
            "opencode",
            "OpenHands",
            "SWE-agent / mini-SWE-agent",
            "Aider",
        ):
            with self.subTest(project=project):
                self.assertIn(project, text)

        self.assertIn("not evidence of endorsement, adoption, integration, or review", text)
        self.assertIn("post-run supplied-record auditor", text)
        self.assertIn("claim-vs-evidence layer", text)
        self.assertIn("approval/sandbox boundary fields", text)
        self.assertIn("--fail-on-reason-code test.required_not_run", text)
        self.assertIn("does not natively ingest Hermes, OpenClaw, opencode", text)
        self.assertIn("does not replace `docs/OUTREACH_TARGETS.md`", text)
        self.assertIn("Add a `docs/RUN_RECORD_FIELD_CHECKLIST.md` only after", text)
        self.assertNotIn("endorsed Evidence Court", text)
        self.assertNotIn("native Hermes ingestion", text)
        self.assertNotIn("10k", text)

    def test_release_manifest_is_the_claim_file_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs" / "EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md"
        text = manifest.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        included_paths = (
            ".github/ISSUE_TEMPLATE/technical-review-request.md",
            ".github/workflows/evidence-court.yml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "docs/CAPABILITY_GATES.md",
            "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md",
            "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
            "docs/EVIDENCE_COURT_COMPARISON.md",
            "docs/TECHNICAL_TREND_RADAR.md",
            "docs/REDACTION_GUIDE.md",
            "docs/CURRENT_PROOF_STATUS.md",
            "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md",
            "docs/EXPERT_REVIEW_BRIEF.md",
            "docs/OUTREACH.md",
            "docs/OUTREACH_TARGETS.md",
            "docs/TECHNICAL_REVIEW_REQUEST.md",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "docs/LAUNCH_POST.md",
            "docs/social-card.svg",
            "docs/RELEASE_NOTES_V0_1_0.md",
            "docs/RELEASE_NOTES_V0_1_1.md",
            "docs/RELEASE_NOTES_V0_1_2.md",
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/bad-run.report.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
            "examples/evidence-court/run-record.schema.json",
            "quantagent/evidence_court.py",
            "quantagent/__init__.py",
            "quantagent/cli.py",
            "scripts/evidence_court_release_set.sh",
            "scripts/evidence_court_smoke.sh",
            "tests/fixtures/evidence_court/marked_bad_transcript.txt",
            "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
            "tests/fixtures/evidence_court/test_outputs/runner_outputs.json",
            "tests/test_evidence_court.py",
            "tests/test_evidence_court_smoke_script.py",
        )
        excluded_paths = (
            "quantagent/agent_planner.py",
            "tests/test_agent_planner_contract.py",
            "tests/test_external_benchmark_multimodule_regression.py",
        )

        for path in included_paths:
            with self.subTest(path=path):
                self.assertIn(f"`{path}`", text)
                self.assertTrue((root / path).exists())

        for path in excluded_paths:
            with self.subTest(path=path):
                self.assertIn(f"`{path}`", text)

        self.assertIn("Only these release files support", text)
        self.assertIn(
            "permissive supplied JSON run-record schema at `examples/evidence-court/run-record.schema.json`",
            text,
        )
        self.assertIn("must not support the Evidence Court v0.1 public claim", normalized)
        self.assertIn("native Claude/Codex/Cursor/Devin transcript ingestion", text)
        self.assertIn("GitHub Actions or CI log ingestion", text)
        self.assertIn("real Node fs/process handling", text)
        self.assertIn("workflow wired locally", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-branch-diff main", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-staged-release-set", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke", text)
        self.assertIn(
            "python -m pytest -p no:cacheprovider tests/test_evidence_court_smoke_script.py tests/test_evidence_court.py -q",
            text,
        )
        self.assertIn("git diff --check", text)
        self.assertIn("evidence-court-smoke", text)
        self.assertIn("artifact-manifest.json", text)
        self.assertIn("jsonl-events.json", text)
        self.assertIn("reviewer-quickstart.md", text)
        self.assertIn("smoke-summary.txt", text)
        self.assertIn("Artifact content check", text)
        self.assertIn("`artifact-manifest.json` lists the safe claim", text)
        self.assertIn("source provenance checks", text)
        self.assertIn("report artifacts include `source: ...`", text)
        self.assertIn("verifies the artifact file set, manifest contract, artifact SHA-256 hashes", text)
        self.assertIn("open `bad-run.md` first", text)
        self.assertIn("`bad-run.md` shows `Verdict: FAIL`", text)
        self.assertIn("`redacted-real-world-bad-run.json` contains `\"verdict\": \"FAIL\"`", text)
        self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", text)
        self.assertIn("`good-run.json` contains `\"verdict\": \"PASS\"`", text)
        self.assertIn("`jsonl-events.json` contains `\"verdict\": \"FAIL\"`", text)
        self.assertIn("`mixed-source-rejection.txt` contains `exit_code=2`", text)
        self.assertIn("green for the PR head commit", text)
        self.assertNotIn("After push, remote GitHub Actions", text)
        self.assertIn("Optional remote artifact download", text)
        self.assertIn(
            "gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn(
            "bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn("sed -n '1,80p' /tmp/evidence-court-smoke/artifact-manifest.json", text)

    def test_supplied_run_record_schema_matches_loader_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema_path = root / "examples" / "evidence-court" / "run-record.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        readme = (root / "README.md").read_text(encoding="utf-8")
        manifest = (root / "docs" / "EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md").read_text(encoding="utf-8")

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["title"], "Evidence Court supplied JSON run record v0.1")
        self.assertTrue(schema["additionalProperties"])
        self.assertIn("not a native Claude/Codex/Cursor/Devin/CI log schema", schema["description"])

        properties = schema["properties"]
        for field in (
            "claimed_task",
            "claim",
            "final_claim",
            "files_read",
            "files_edited",
            "commands_run",
            "test_output",
            "allowed_edit_paths",
            "allowed_files",
            "protected_paths",
            "required_tests",
            "required_commands",
            "source",
        ):
            with self.subTest(field=field):
                self.assertIn(field, properties)

        command_text = json.dumps(schema["$defs"]["command"], sort_keys=True)
        for field in ("command", "cmd", "argv", "test_output", "output", "stdout", "stderr"):
            with self.subTest(command_field=field):
                self.assertIn(field, command_text)

        for example_name in ("bad-run.json", "good-run.json", "redacted-real-world-bad-run.json"):
            with self.subTest(example_name=example_name):
                payload = json.loads((root / "examples" / "evidence-court" / example_name).read_text(encoding="utf-8"))
                for field in ("claimed_task", "final_claim", "files_read", "files_edited", "commands_run"):
                    self.assertIn(field, payload)

        self.assertIn("examples/evidence-court/run-record.schema.json", readme)
        self.assertIn("examples/evidence-court/run-record.schema.json", manifest)
        forbidden = (
            "native Claude ingestion is supported",
            "native Codex ingestion is supported",
            "native CI log ingestion is supported",
            "endorsed by",
            "10k",
            "10000",
        )
        combined = json.dumps(schema, ensure_ascii=False) + "\n" + readme + "\n" + manifest
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

    def test_launch_packet_keeps_public_claims_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        launch_packet = root / "docs" / "EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md"
        text = launch_packet.read_text(encoding="utf-8")
        normalized = " ".join(text.split())

        self.assertIn("mako evidence-court --demo bad-run", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke", text)
        self.assertIn(
            "Evidence Court audits supplied structured JSON run records, explicit marked",
            text,
        )
        self.assertIn("Marked transcript v0 is an explicit marker format.", text)
        self.assertIn(
            "Remote CI evidence requires GitHub Actions `Evidence Court Smoke` green for the PR head commit.",
            text,
        )
        self.assertIn("## Retweet Copy", text)
        self.assertIn("It is not another coding agent.", text)
        self.assertIn("claim-vs-evidence gate for supplied agent-run records", text)
        self.assertIn("## What Normal Tests Miss", text)
        self.assertIn("Test output alone cannot tell whether the agent reported the required test", text)
        self.assertIn("edited protected tests, changed files outside scope", text)
        self.assertIn("goes beyond the supplied evidence", text)
        self.assertIn("It audits whether the record supports the claim.", text)
        self.assertIn("missing reported required tests", normalized)
        self.assertIn(
            "protected-file edits, out-of-scope changes, and unsupported success claims",
            normalized,
        )
        self.assertIn("Do not say:", text)
        self.assertIn("Native Claude/Codex/Cursor/Devin ingestion is supported.", text)
        self.assertIn("CI logs / GitHub Actions logs are ingested.", text)
        self.assertIn("inside the supplied record", text)
        self.assertIn("not \"another agent\"", normalized)
        safe_copy = text.split("Do not say:", 1)[0]
        forbidden_positive_claims = (
            "Native Claude/Codex/Cursor/Devin ingestion is supported.",
            "CI logs / GitHub Actions logs are ingested.",
            "CI is green",
            "OpenMako proves broad SWE-style repository repair.",
            "OpenMako has achieved Desktop L4/L5 autonomy.",
            "Evidence Court proves tests really ran outside the supplied record.",
        )
        for claim in forbidden_positive_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, safe_copy)
        self.assertNotIn("pushed workflow run", safe_copy)
        self.assertIn("## PR Checklist", text)
        included_section = text.split("### Included Files", 1)[1].split("### Excluded From This Claim", 1)[0]
        self.assertIn("- [ ] `docs/REDACTION_GUIDE.md`", included_section)
        self.assertIn("- [ ] `examples/evidence-court/redacted-real-world-bad-run.json`", included_section)
        self.assertIn("- [ ] `scripts/evidence_court_smoke.sh`", included_section)
        self.assertNotIn("`bash scripts/evidence_court_smoke.sh`", included_section)
        self.assertIn("`docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md`", text)
        self.assertIn("`docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-staged-release-set", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-branch-diff main", text)
        self.assertIn("GitHub Actions `Evidence Court Smoke` is green for the PR head commit.", text)
        self.assertIn("after a green PR workflow for the PR head", text)
        self.assertIn("evidence-court-smoke", text)
        self.assertIn("reviewer-quickstart.md", text)
        self.assertIn("smoke-summary.txt", text)
        self.assertIn("Artifact content check", text)
        self.assertIn("open `bad-run.md` first", text)
        self.assertIn("source provenance checks", text)
        self.assertIn("report artifacts include `source: ...`", text)
        self.assertIn("`fail-on-fail.json` contains `\"verdict\": \"FAIL\"`", text)
        self.assertIn("written only after `--fail-on fail` exits 1", text)
        self.assertIn("The PR body must include the same 30-second reviewer path", text)
        self.assertIn("`bad-run.md` shows `Verdict: FAIL`", text)
        self.assertIn("`redacted-real-world-bad-run.json` shows `\"verdict\": \"FAIL\"`", text)
        self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", text)
        self.assertIn("`good-run.json` shows `\"verdict\": \"PASS\"`", text)
        self.assertIn("openmako-agent-run-result.json", text)
        self.assertIn("source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json", text)
        self.assertIn("`mixed-source-rejection.txt` shows", text)
        self.assertIn("Optional remote artifact download", text)
        self.assertIn("### Local Artifact Review Path", text)
        self.assertIn("Before remote CI exists:", text)
        self.assertIn("sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md", text)
        self.assertIn(
            "gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn("## Post-PR Public Gate", text)
        self.assertIn("Record the PR URL and PR head SHA before updating any public proof file.", text)
        self.assertIn(
            "Wait for GitHub Actions `Evidence Court Smoke` to finish on the PR head",
            text,
        )
        self.assertIn(
            "Update `docs/CURRENT_PROOF_STATUS.md` only after the remote evidence URL,",
            text,
        )
        self.assertIn("run id, commit SHA, and artifact check are known.", text)
        self.assertIn(
            "Do not mark outreach as `sent`, `replied`, or `shared` without a public",
            text,
        )
        self.assertIn("evidence URL for that status.", text)
        self.assertIn(
            "Do not ask trend-watch targets for promotion before PR-head CI evidence",
            text,
        )
        self.assertIn(
            "Do not state external review, endorsement, adoption, share, 10k stars, or",
            text,
        )
        self.assertIn("10000 stars without evidence URLs.", text)
        self.assertIn("`quantagent/agent_planner.py`", text)
        self.assertIn("`tests/test_external_benchmark_multimodule_regression.py`", text)

    def test_capability_gates_use_bash_smoke_invocation(self) -> None:
        root = Path(__file__).resolve().parents[1]
        capability_gates = root / "docs" / "CAPABILITY_GATES.md"
        text = capability_gates.read_text(encoding="utf-8")

        self.assertIn("bash scripts/evidence_court_smoke.sh", text)
        self.assertNotIn("run `scripts/evidence_court_smoke.sh` locally", text)
        self.assertIn('"This repository ships the broader OpenMako coding agent runtime."', text)
        self.assertIn("Desktop, quant trading, planner, or autonomous repair capability is proven", text)
        self.assertNotIn("Programming evidence exists on internal hidden and repeat-stability packs.", text)
        self.assertNotIn("Programming repair improves under evidence", text)
        self.assertNotIn("fixture proves plan", text)

    def test_pr_body_is_copyable_and_keeps_claims_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pr_body = root / "docs" / "EVIDENCE_COURT_V0_1_PR_BODY.md"
        text = pr_body.read_text(encoding="utf-8")
        normalized = " ".join(text.split())

        self.assertIn("Copy this into the GitHub PR body", text)
        self.assertIn("````markdown", text)
        self.assertIn("OpenMako Evidence Court audits supplied structured JSON run records", text)
        self.assertIn("inside the supplied record", text)
        self.assertIn("mako evidence-court --demo bad-run", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh", text)
        self.assertIn("bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke", text)
        self.assertIn("### 30-Second Reviewer Path", text)
        self.assertIn("`bad-run.md`: the supplied record claims success", text)
        self.assertIn("`redacted-real-world-bad-run.json`: a redacted supplied record claims success", text)
        self.assertIn("`fail-on-fail.json`: the same bad run under `--fail-on fail` exits 1", text)
        self.assertIn("`artifact-manifest.json`: safe claim", text)
        self.assertIn("`reviewer-quickstart.md`: copy-paste local/remote review path", text)
        self.assertIn("`openmako-agent-run-result.json`: explicit OpenMako AgentRunResult producer-artifact input", text)
        self.assertIn("`jsonl-events.json`: explicit Evidence Court JSONL event-stream input", text)
        self.assertIn("`mixed-source-rejection.txt`: mixed inputs fail closed with `exit_code=2`", text)
        self.assertIn("`examples/evidence-court/run-record.schema.json`: permissive supplied-record schema", text)
        self.assertIn("`docs/TECHNICAL_TREND_RADAR.md`: current local-agent/coding-agent trend inputs", text)
        self.assertIn("not evidence of endorsement, adoption, integration, or review", text)
        self.assertIn("not a native vendor-log schema", text)
        included_section = text.split("### Included In This Release Claim", 1)[1].split("### Excluded From This Claim", 1)[0]
        self.assertIn("- `scripts/evidence_court_smoke.sh`", included_section)
        self.assertIn("- `examples/evidence-court/run-record.schema.json`", included_section)
        self.assertIn("- `docs/TECHNICAL_TREND_RADAR.md`", included_section)
        self.assertNotIn("`bash scripts/evidence_court_smoke.sh`", included_section)
        self.assertIn("`docs/EVIDENCE_COURT_V0_1_PR_BODY.md`", text)
        self.assertIn("`docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-staged-release-set", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --audit-staged-claim-copy", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke", text)
        self.assertIn("bash scripts/evidence_court_release_set.sh --check-branch-diff main", text)
        self.assertIn("GitHub Actions `Evidence Court Smoke` is green for the PR head commit.", text)
        self.assertIn("evidence-court-smoke", text)
        self.assertIn("reviewer-quickstart.md", text)
        self.assertIn("smoke-summary.txt", text)
        self.assertIn("Artifact content check", text)
        self.assertIn("passes on the downloaded artifact directory", text)
        self.assertIn("open `bad-run.md` first", text)
        self.assertIn("`bad-run.md` shows `Verdict: FAIL`", text)
        self.assertIn("`redacted-real-world-bad-run.json` shows `\"verdict\": \"FAIL\"`", text)
        self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", text)
        self.assertIn("`good-run.json` shows `\"verdict\": \"PASS\"`", text)
        self.assertIn("openmako-agent-run-result.json", text)
        self.assertIn("source: tests/fixtures/evidence_court/openmako_agent_run_result_bad.json", text)
        self.assertIn("`mixed-source-rejection.txt` shows", text)
        self.assertIn("Optional remote artifact download", text)
        self.assertIn("### Local Artifact Review Path", text)
        self.assertIn("Before remote CI exists:", text)
        self.assertIn("fail-on-fail.json", text)
        self.assertIn(
            "bash scripts/evidence_court_release_set.sh --verify-artifact-dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn("sed -n '1,80p' /tmp/evidence-court-smoke/reviewer-quickstart.md", text)
        self.assertIn(
            "gh run download <run-id> --name evidence-court-smoke --dir /tmp/evidence-court-smoke",
            text,
        )
        self.assertIn("`quantagent/agent_planner.py`", text)
        self.assertIn("do not support the Evidence Court v0.1 public claim", normalized)
        self.assertIn("examples/evidence-court/run-record.schema.json", text)
        self.assertIn("Retweet-sized version:", text)
        self.assertIn("claim-vs-evidence gate for supplied agent-run records", text)
        self.assertIn("protected-file edits, out-of-scope", text)
        self.assertIn("unsupported success claims", text)
        self.assertEqual(text.count("````markdown"), 1)
        self.assertTrue(text.rstrip().endswith("````"))
        self.assertIn("bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke\n```", text)

        safe_section = text.split("### Excluded From This Claim", 1)[0]
        forbidden_positive_claims = (
            "native Claude/Codex/Cursor/Devin/CI log ingestion is supported",
            "Evidence Court proves tests really ran outside the supplied record",
            "OpenMako proves broad SWE-style repository repair",
            "OpenMako has achieved Desktop L4/L5 autonomy",
        )
        for claim in forbidden_positive_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, safe_section)

    def test_release_set_script_lists_and_checks_staging_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_release_set.sh"

        list_proc = subprocess.run(
            ["bash", str(script), "--list"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(list_proc.returncode, 0, list_proc.stdout + list_proc.stderr)
        self.assertIn("scripts/evidence_court_release_set.sh", list_proc.stdout)
        self.assertIn("quantagent/agent_planner.py", list_proc.stdout)

        check_proc = subprocess.run(
            ["bash", str(script), "--check"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(check_proc.returncode, 0, check_proc.stdout + check_proc.stderr)
        self.assertNotIn("excluded file is staged", check_proc.stdout + check_proc.stderr)

    def test_release_set_script_rejects_bad_staging_without_touching_real_index(self) -> None:
        root = Path(__file__).resolve().parents[1]
        real_index_before = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(real_index_before.returncode, 0, real_index_before.stdout + real_index_before.stderr)

        included = self._run_release_set_with_staged_paths(root, "README.md")
        self.assertEqual(included.returncode, 0, included.stdout + included.stderr)
        self.assertIn("Staged files are within the Evidence Court v0.1 release set.", included.stdout)

        script = root / "scripts" / "evidence_court_release_set.sh"
        env = os.environ.copy()
        with tempfile.TemporaryDirectory(prefix="openmako-release-index-") as tmp:
            env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
            read_tree = subprocess.run(
                ["git", "read-tree", "HEAD"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(read_tree.returncode, 0, read_tree.stdout + read_tree.stderr)
            self._stage_synthetic_blob(
                root,
                env,
                "quantagent/agent_planner.py",
                "# synthetic excluded staged file for Evidence Court release-set test\n",
            )
            excluded = subprocess.run(
                ["bash", str(script), "--check"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
        self.assertNotEqual(excluded.returncode, 0, excluded.stdout + excluded.stderr)
        self.assertIn(
            "excluded file is staged for Evidence Court v0.1: quantagent/agent_planner.py",
            excluded.stdout + excluded.stderr,
        )

        unexpected_path = root / ".tmp_evidence_court_unexpected_stage.md"
        unexpected_path.write_text("not part of the Evidence Court v0.1 release set\n", encoding="utf-8")
        try:
            unexpected = self._run_release_set_with_staged_paths(root, unexpected_path.name)
        finally:
            unexpected_path.unlink(missing_ok=True)
        self.assertNotEqual(unexpected.returncode, 0, unexpected.stdout + unexpected.stderr)
        self.assertIn(
            f"unexpected staged file for Evidence Court v0.1: {unexpected_path.name}",
            unexpected.stdout + unexpected.stderr,
        )

        real_index_after = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(real_index_after.returncode, 0, real_index_after.stdout + real_index_after.stderr)
        self.assertEqual(real_index_before.stdout, real_index_after.stdout)

    def test_release_set_script_requires_complete_staged_release_set_when_requested(self) -> None:
        root = Path(__file__).resolve().parents[1]
        release_paths = (
            ".github/ISSUE_TEMPLATE/technical-review-request.md",
            ".github/workflows/evidence-court.yml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "docs/CAPABILITY_GATES.md",
            "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md",
            "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
            "docs/EVIDENCE_COURT_COMPARISON.md",
            "docs/TECHNICAL_TREND_RADAR.md",
            "docs/REDACTION_GUIDE.md",
            "docs/CURRENT_PROOF_STATUS.md",
            "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md",
            "docs/EXPERT_REVIEW_BRIEF.md",
            "docs/OUTREACH.md",
            "docs/OUTREACH_TARGETS.md",
            "docs/TECHNICAL_REVIEW_REQUEST.md",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "docs/LAUNCH_POST.md",
            "docs/social-card.svg",
            "docs/RELEASE_NOTES_V0_1_0.md",
            "docs/RELEASE_NOTES_V0_1_1.md",
            "docs/RELEASE_NOTES_V0_1_2.md",
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/bad-run.report.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
            "examples/evidence-court/run-record.schema.json",
            "quantagent/evidence_court.py",
            "quantagent/__init__.py",
            "quantagent/cli.py",
            "scripts/evidence_court_release_set.sh",
            "scripts/evidence_court_smoke.sh",
            "tests/fixtures/evidence_court/marked_bad_transcript.txt",
            "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
            "tests/fixtures/evidence_court/test_outputs/runner_outputs.json",
            "tests/test_evidence_court.py",
            "tests/test_evidence_court_smoke_script.py",
        )

        empty = self._run_release_set_with_staged_paths(root, mode="--check-staged-release-set")
        self.assertNotEqual(empty.returncode, 0, empty.stdout + empty.stderr)
        self.assertIn(
            "missing staged release file for Evidence Court v0.1: .github/workflows/evidence-court.yml",
            empty.stdout + empty.stderr,
        )
        self.assertNotIn("unbound variable", empty.stdout + empty.stderr)

        complete = self._run_release_set_with_staged_paths(
            root,
            *release_paths,
            mode="--check-staged-release-set",
        )
        self.assertEqual(complete.returncode, 0, complete.stdout + complete.stderr)
        self.assertIn("Staged files exactly cover the Evidence Court v0.1 release set.", complete.stdout)

        progress_bookkeeping = self._run_release_set_with_staged_paths(root, "PROGRESS.md")
        self.assertEqual(progress_bookkeeping.returncode, 0, progress_bookkeeping.stdout + progress_bookkeeping.stderr)
        self.assertIn("Staged files are within the Evidence Court v0.1 release set.", progress_bookkeeping.stdout)

        progress_in_exact_set = self._run_release_set_with_staged_paths(
            root,
            *release_paths,
            "PROGRESS.md",
            mode="--check-staged-release-set",
        )
        self.assertNotEqual(progress_in_exact_set.returncode, 0, progress_in_exact_set.stdout + progress_in_exact_set.stderr)
        self.assertIn(
            "PROGRESS.md is not allowed in the exact Evidence Court v0.1 staged release set",
            progress_in_exact_set.stdout + progress_in_exact_set.stderr,
        )
        self.assertNotIn("Staged files exactly cover the Evidence Court v0.1 release set.", progress_in_exact_set.stdout)

        incomplete = self._run_release_set_with_staged_paths(
            root,
            "LICENSE",
            "README.md",
            mode="--check-staged-release-set",
        )
        self.assertNotEqual(incomplete.returncode, 0, incomplete.stdout + incomplete.stderr)
        self.assertIn(
            "missing staged release file for Evidence Court v0.1: .github/workflows/evidence-court.yml",
            incomplete.stdout + incomplete.stderr,
        )

    def test_release_set_script_audits_staged_claim_copy(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "scripts" / "evidence_court_release_set.sh"
        release_paths = (
            ".github/ISSUE_TEMPLATE/technical-review-request.md",
            ".github/workflows/evidence-court.yml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "docs/CAPABILITY_GATES.md",
            "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md",
            "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
            "docs/EVIDENCE_COURT_COMPARISON.md",
            "docs/TECHNICAL_TREND_RADAR.md",
            "docs/REDACTION_GUIDE.md",
            "docs/CURRENT_PROOF_STATUS.md",
            "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md",
            "docs/EXPERT_REVIEW_BRIEF.md",
            "docs/OUTREACH.md",
            "docs/OUTREACH_TARGETS.md",
            "docs/TECHNICAL_REVIEW_REQUEST.md",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "docs/LAUNCH_POST.md",
            "docs/social-card.svg",
            "docs/RELEASE_NOTES_V0_1_0.md",
            "docs/RELEASE_NOTES_V0_1_1.md",
            "docs/RELEASE_NOTES_V0_1_2.md",
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/bad-run.report.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
            "examples/evidence-court/run-record.schema.json",
            "quantagent/evidence_court.py",
            "quantagent/__init__.py",
            "quantagent/cli.py",
            "scripts/evidence_court_release_set.sh",
            "scripts/evidence_court_smoke.sh",
            "tests/fixtures/evidence_court/marked_bad_transcript.txt",
            "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
            "tests/fixtures/evidence_court/test_outputs/runner_outputs.json",
            "tests/test_evidence_court.py",
            "tests/test_evidence_court_smoke_script.py",
        )
        env = os.environ.copy()
        with tempfile.TemporaryDirectory(prefix="openmako-claim-copy-index-") as tmp:
            env["GIT_INDEX_FILE"] = str(Path(tmp) / "index")
            read_tree = subprocess.run(
                ["git", "read-tree", "HEAD"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(read_tree.returncode, 0, read_tree.stdout + read_tree.stderr)
            for path in release_paths:
                self._stage_synthetic_blob(
                    root,
                    env,
                    path,
                    (root / path).read_text(encoding="utf-8") + "\n",
                )

            audit = subprocess.run(
                ["bash", str(script), "--audit-staged-claim-copy"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            self.assertIn("Staged Evidence Court public claim copy keeps the v0.1 boundaries.", audit.stdout)

            pr_body = root / "docs" / "EVIDENCE_COURT_V0_1_PR_BODY.md"
            weakened_text = pr_body.read_text(encoding="utf-8").replace(
                "- `docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md`\n",
                "",
            )
            blob = subprocess.run(
                ["git", "hash-object", "-w", "--stdin"],
                cwd=root,
                env=env,
                input=weakened_text,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(blob.returncode, 0, blob.stdout + blob.stderr)
            update = subprocess.run(
                [
                    "git",
                    "update-index",
                    "--cacheinfo",
                    "100644",
                    blob.stdout.strip(),
                    "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(update.returncode, 0, update.stdout + update.stderr)
            weakened_audit = subprocess.run(
                ["bash", str(script), "--audit-staged-claim-copy"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertNotEqual(weakened_audit.returncode, 0, weakened_audit.stdout + weakened_audit.stderr)
            self.assertIn(
                "staged claim-copy audit missing in docs/EVIDENCE_COURT_V0_1_PR_BODY.md: docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
                weakened_audit.stdout + weakened_audit.stderr,
            )
        self.assertIn(
            "examples/evidence-court/run-record.schema.json",
            (root / "docs" / "EVIDENCE_COURT_V0_1_PR_BODY.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "docs/TECHNICAL_TREND_RADAR.md",
            (root / "docs" / "EVIDENCE_COURT_V0_1_PR_BODY.md").read_text(encoding="utf-8"),
        )

    def test_release_set_script_checks_committed_branch_diff(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source_script = root / "scripts" / "evidence_court_release_set.sh"
        release_paths = (
            ".github/ISSUE_TEMPLATE/technical-review-request.md",
            ".github/workflows/evidence-court.yml",
            "LICENSE",
            "README.md",
            "pyproject.toml",
            "docs/CAPABILITY_GATES.md",
            "docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md",
            "docs/EVIDENCE_COURT_V0_1_PR_BODY.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_CUT.md",
            "docs/EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md",
            "docs/EVIDENCE_COURT_COMPARISON.md",
            "docs/TECHNICAL_TREND_RADAR.md",
            "docs/REDACTION_GUIDE.md",
            "docs/CURRENT_PROOF_STATUS.md",
            "docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md",
            "docs/EXPERT_REVIEW_BRIEF.md",
            "docs/OUTREACH.md",
            "docs/OUTREACH_TARGETS.md",
            "docs/TECHNICAL_REVIEW_REQUEST.md",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "docs/LAUNCH_POST.md",
            "docs/social-card.svg",
            "docs/RELEASE_NOTES_V0_1_0.md",
            "docs/RELEASE_NOTES_V0_1_1.md",
            "docs/RELEASE_NOTES_V0_1_2.md",
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/bad-run.report.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
            "examples/evidence-court/run-record.schema.json",
            "quantagent/evidence_court.py",
            "quantagent/__init__.py",
            "quantagent/cli.py",
            "scripts/evidence_court_release_set.sh",
            "scripts/evidence_court_smoke.sh",
            "tests/fixtures/evidence_court/marked_bad_transcript.txt",
            "tests/fixtures/evidence_court/openmako_agent_run_result_bad.json",
            "tests/fixtures/evidence_court/test_outputs/runner_outputs.json",
            "tests/test_evidence_court.py",
            "tests/test_evidence_court_smoke_script.py",
        )

        with tempfile.TemporaryDirectory(prefix="openmako-branch-diff-") as tmp:
            repo = Path(tmp)
            script = repo / "scripts" / "evidence_court_release_set.sh"
            for path in release_paths:
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                if path == "scripts/evidence_court_release_set.sh":
                    target.write_text(source_script.read_text(encoding="utf-8"), encoding="utf-8")
                else:
                    target.write_text(f"baseline {path}\n", encoding="utf-8")

            self._git(repo, "init", "-b", "main")
            self._git(repo, "add", "--", ".")
            self._git(repo, "commit", "-m", "baseline")
            self._git(repo, "checkout", "-b", "evidence-court-release")

            (repo / "README.md").write_text("release readme change\n", encoding="utf-8")
            self._git(repo, "add", "--", "README.md")
            self._git(repo, "commit", "-m", "release-only change")
            clean = subprocess.run(
                ["bash", str(script), "--check-branch-diff", "main"],
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            self.assertIn("Branch diff against main is limited to the Evidence Court v0.1 release set.", clean.stdout)

            planner = repo / "quantagent" / "agent_planner.py"
            planner.write_text("unrelated planner change\n", encoding="utf-8")
            self._git(repo, "add", "--", "quantagent/agent_planner.py")
            self._git(repo, "commit", "-m", "leak planner change")
            leaked = subprocess.run(
                ["bash", str(script), "--check-branch-diff", "main"],
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertNotEqual(leaked.returncode, 0, leaked.stdout + leaked.stderr)
            self.assertIn(
                "excluded file is in branch diff for Evidence Court v0.1: quantagent/agent_planner.py",
                leaked.stdout + leaked.stderr,
            )

    def _git(self, cwd: Path, *args: str) -> None:
        proc = subprocess.run(
            [
                "git",
                "-c",
                "user.name=OpenMako Test",
                "-c",
                "user.email=openmako-test@example.invalid",
                *args,
            ],
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_readme_separates_other_modules_from_v0_1_launch_claim(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("docs/EVIDENCE_COURT_V0_1_LAUNCH_PACKET.md", readme)
        self.assertIn("Audit whether a coding agent's success claim is supported by a supplied run record.", readme)
        self.assertIn("not another coding agent", readme)
        self.assertIn("claim-vs-evidence gate", readme)
        self.assertIn("reports from the supplied record", readme)
        self.assertIn("## Review In 30 Seconds", readme)
        self.assertIn("After a green PR-head GitHub Actions run, download the `evidence-court-smoke` artifact", readme)
        self.assertIn("bash scripts/evidence_court_smoke.sh --artifact-dir /tmp/evidence-court-smoke", readme)
        self.assertIn("/tmp/evidence-court-smoke/reviewer-quickstart.md", readme)
        self.assertNotIn("After a pushed GitHub Actions run", readme)
        self.assertIn("do not claim remote CI evidence", readme)
        self.assertIn("The bad demo is a supplied run record", readme)
        self.assertIn("This is the smallest evidence check: a bad supplied record says tests passed", readme)
        self.assertIn("protected test edit and no reported required pytest command", readme)
        self.assertIn("test output status reason: no known pass/fail pattern matched", readme)
        self.assertIn("[`examples/evidence-court/bad-run.report.json`](examples/evidence-court/bad-run.report.json)", readme)
        self.assertIn("To block CI on this verdict, run the same command with `--fail-on fail`", readme)
        self.assertIn("the bad run exits 1 instead of report-only 0", readme)
        self.assertIn("## What Normal Tests Miss", readme)
        self.assertIn("ordinary test\noutput does not settle", readme)
        self.assertIn("did the run report the required test command, or only a weaker command?", readme)
        self.assertIn("did it edit protected tests or out-of-scope files?", readme)
        self.assertIn("did the final claim go beyond the supplied test evidence?", readme)
        self.assertIn("It audits\nwhether the supplied record supports the agent's claim.", readme)
        self.assertIn("does not parse raw chat transcripts or native Claude/Codex/Cursor/Devin/CI logs", readme)
        self.assertIn("examples/evidence-court/run-record.schema.json", readme)
        self.assertIn("Adapter authors can start from the permissive schema", readme)
        self.assertIn("It is not a native vendor-log schema.", readme)
        self.assertIn("sampled runner output support, not a universal test-runner or CI-log parser", readme)
        self.assertIn("# From a checkout of this repository:", readme)
        self.assertIn("This public repository contains the Evidence Court v0.1 release set only.", readme)
        self.assertIn("does not ship or claim the broader OpenMako agent runtime", readme)
        self.assertNotIn("not a toy", readme)
        self.assertNotIn("writes proof artifacts", readme)
        first_screen = "\n".join(readme.splitlines()[:30])
        self.assertIn("Agent Evidence Harness for coding agents.", first_screen)
        self.assertIn("anti-fake-progress gate", first_screen)
        self.assertIn("not another coding agent", first_screen)
        self.assertIn("not a codegraph, not a token compressor, and not an agent skill library", first_screen)
        self.assertIn("record auditor", first_screen)
        self.assertIn("claim-vs-evidence gate", first_screen)
        self.assertIn("mako evidence-court --demo bad-run", first_screen)
        self.assertIn("# Verdict: FAIL", first_screen)
        self.assertIn("--fail-on fail", first_screen)
        demo_block = readme.split("## 10-Second Demo", 1)[1].split("## Quick Start", 1)[0]
        self.assertIn("mako evidence-court --demo bad-run", demo_block)
        self.assertIn("test output status reason: no known pass/fail pattern matched", demo_block)
        self.assertIn("To block CI on this verdict", demo_block)
        self.assertNotIn("pip install", demo_block)
        quick_start = readme.split("## Quick Start", 1)[1].split("## What It Checks", 1)[0]
        self.assertIn("# From a checkout of this repository:", quick_start)
        self.assertIn("python3 -m pip install .", quick_start)
        self.assertLess(readme.index("## 10-Second Demo"), readme.index("## Quick Start"))
        self.assertLess(readme.index("mako evidence-court --demo bad-run"), readme.index("python3 -m pip install ."))
        self.assertLess(readme.index("# Verdict: FAIL"), readme.index("## Quick Start"))
        self.assertNotIn("<your-openmako-repo-url>", readme)
        self.assertNotIn("## Other OpenMako Modules", readme)
        self.assertNotIn("<summary>Other OpenMako modules outside the Evidence Court v0.1 launch claim</summary>", readme)
        self.assertNotIn("mako doctor", readme)
        self.assertNotIn("mako fix", readme)
        self.assertNotIn("Extreme Planner", readme)

    def test_readme_bad_run_demo_excerpt_matches_cli_output(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        demo_block = readme.split("## 10-Second Demo", 1)[1].split("## Quick Start", 1)[0]
        demo_block = demo_block.split("```bash", 1)[1].split("```", 1)[0]
        demo_lines = [line.strip() for line in demo_block.splitlines() if line.strip() and not line.startswith("```")]

        self.assertIn("mako evidence-court --demo bad-run", demo_lines)
        proc = subprocess.run(
            [sys.executable, "-m", "quantagent.cli", "--no-trust-prompt", "evidence-court", "--demo", "bad-run"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        cli_output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, cli_output)

        for line in demo_lines:
            if line == "mako evidence-court --demo bad-run" or line.startswith("# CI gate:"):
                continue
            if line.startswith("# Claim: "):
                self.assertIn(f"- {line.removeprefix('# Claim: ')}", cli_output)
                continue
            if line.startswith("# Evidence: "):
                self.assertIn(line.removeprefix("# Evidence: "), cli_output)
                continue
            if line.startswith("# Verdict: "):
                self.assertIn(f"## Verdict: {line.removeprefix('# Verdict: ')}", cli_output)
                continue
            self.fail(f"Unhandled README bad-run demo line: {line}")

    def test_readme_json_report_excerpt_matches_cli_output(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        section = readme.split("Machine-readable bad-run excerpt", 1)[1].split("Try the same path", 1)[0]
        excerpt = json.loads(section.split("```json", 1)[1].split("```", 1)[0])

        self.assertEqual(set(excerpt), {"schema_version", "verdict", "test_verification"})
        self.assertIn("excerpt, not the full report", section)
        self.assertIn(
            "[`examples/evidence-court/bad-run.report.json`](examples/evidence-court/bad-run.report.json)",
            readme,
        )
        self.assertTrue((root / "examples" / "evidence-court" / "bad-run.report.json").exists())

        proc = subprocess.run(
            [sys.executable, "-m", "quantagent.cli", "--no-trust-prompt", "evidence-court", "--demo", "bad-run", "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        cli_payload = json.loads(proc.stdout)

        self.assertEqual(excerpt["schema_version"], cli_payload["schema_version"])
        self.assertEqual(excerpt["verdict"], cli_payload["verdict"])
        self.assertEqual(excerpt["test_verification"], cli_payload["test_verification"])
        self.assertEqual(excerpt["schema_version"], "evidence-court.report.v0.1")
        self.assertEqual(excerpt["verdict"], "FAIL")
        self.assertIn(
            "test output status reason: no known pass/fail pattern matched",
            excerpt["test_verification"],
        )

    def test_bad_run_report_fixture_matches_cli_json_output(self) -> None:
        root = Path(__file__).resolve().parents[1]
        report_path = root / "examples" / "evidence-court" / "bad-run.report.json"
        input_path = "examples/evidence-court/bad-run.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))

        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "quantagent.cli",
                "--no-trust-prompt",
                "evidence-court",
                "--input",
                input_path,
                "--json",
            ],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(report, json.loads(proc.stdout))
        self.assertEqual(report["schema_version"], "evidence-court.report.v0.1")
        self.assertEqual(report["verdict"], "FAIL")
        self.assertIn("source: examples/evidence-court/bad-run.json", report["evidence"])
        self.assertIn(
            "test output status reason: no known pass/fail pattern matched",
            report["test_verification"],
        )

        manifest = (root / "docs" / "EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md").read_text(encoding="utf-8")
        self.assertIn("examples/evidence-court/bad-run.report.json", manifest)
        self.assertIn("full generated JSON report fixture", manifest)

    def test_comparison_page_shows_what_normal_tests_miss_without_overclaiming(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        comparison = (root / "docs" / "EVIDENCE_COURT_COMPARISON.md").read_text(encoding="utf-8")

        self.assertIn("docs/EVIDENCE_COURT_COMPARISON.md", readme)
        self.assertIn("What Evidence Court Catches That Normal Tests Miss", comparison)
        self.assertIn("Normal test output can say whether a command passed", comparison)
        self.assertIn("Evidence Court only audits the supplied record", comparison)
        self.assertIn("does not prove tests actually ran outside", comparison)
        self.assertIn("does not natively ingest Claude/Codex/Cursor/Devin/CI logs", comparison)
        self.assertEqual(len(re.findall(r"^## Case \d:", comparison, flags=re.MULTILINE)), 3)

        required_phrases = (
            "mako evidence-court --input examples/evidence-court/bad-run.json",
            "mako evidence-court --demo bad-run",
            "/tmp/evidence-court-weak-test.json",
            "python -m pytest tests/test_unrelated.py -q",
            "required test not run: python -m pytest tests/test_calculator.py -q",
            "edited protected path: tests/test_calculator.py",
            "broad benchmark or real-world repair accuracy",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, comparison)

        lower = comparison.lower()
        forbidden = (
            "better than claude",
            "better than codex",
            "better than cursor",
            "better than openhands",
            "replaces ci",
            "replaces pytest",
            "native claude ingestion is supported",
            "native codex ingestion is supported",
            "proves tests really ran outside",
            "guarantees correctness",
            "broad benchmark accuracy is proven",
            "real-world repair accuracy is proven",
            "10k",
            "endorsed by",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, lower)

    def test_redaction_guide_keeps_realistic_fixtures_shareable_without_overclaiming(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        guide = (root / "docs" / "REDACTION_GUIDE.md").read_text(encoding="utf-8")
        fixture = (root / "examples" / "evidence-court" / "redacted-real-world-bad-run.json").read_text(
            encoding="utf-8"
        )

        self.assertIn("docs/REDACTION_GUIDE.md", readme)
        self.assertIn("redaction guide", readme)
        self.assertIn("mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json", readme)
        self.assertIn("mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json", guide)
        self.assertIn("[REDACTED_REPO]", guide)
        self.assertIn("[REDACTED_LOG_EXCERPT]", guide)
        self.assertIn("Evidence Court only audits the supplied record", guide)
        self.assertIn("not native Claude/Codex/Cursor/Devin/CI", guide)
        self.assertIn("does not prove tests actually ran outside", guide)
        self.assertIn("does not claim broad benchmark or real-world repair accuracy", guide)
        self.assertIn("[REDACTED_REPO]", fixture)
        self.assertIn("[REDACTED_LOG_EXCERPT]", fixture)

        forbidden = (
            "real production incident",
            "proves agents lie",
            "native Claude ingestion",
            "native Codex ingestion",
            "proves tests ran outside",
            "benchmark-realistic proof",
            "unredacted customer data is safe",
            "endorsed by",
            "10k",
        )
        combined = f"{guide}\n{fixture}".lower()
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                if phrase == "real production incident":
                    self.assertIn("does not prove a real production incident", guide)
                    continue
                self.assertNotIn(phrase.lower(), combined)

    def test_current_proof_status_and_review_issue_draft_do_not_overclaim_remote_evidence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        proof_status = (root / "docs" / "CURRENT_PROOF_STATUS.md").read_text(encoding="utf-8")
        issue_draft = (root / "docs" / "TECHNICAL_REVIEW_ISSUE_DRAFT.md").read_text(encoding="utf-8")

        self.assertIn("docs/CURRENT_PROOF_STATUS.md", readme)
        self.assertIn("docs/TECHNICAL_REVIEW_ISSUE_DRAFT.md", readme)
        self.assertIn("Remote CI evidence is confirmed for proof anchor commit `cb1ab5e`", proof_status)
        self.assertIn("not an automatically updated status page", proof_status)
        self.assertIn("actions/runs/26836126047", proof_status)
        self.assertIn("Status Success", proof_status)
        self.assertIn("sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac", proof_status)
        self.assertIn("does not prove the latest main commit", proof_status)
        self.assertIn("does not automatically prove later commits on `main`", proof_status)
        self.assertIn("third-party adoption, endorsement, or review", proof_status)
        self.assertIn("not an endorsement request", issue_draft)
        self.assertIn("Do not treat this draft as a sent review request", issue_draft)
        self.assertIn("Open `docs/CURRENT_PROOF_STATUS.md` before trusting remote CI claims", issue_draft)
        self.assertIn("Current proof-anchor evidence", issue_draft)
        self.assertIn("Evidence Court Smoke run: https://github.com/1966536805l-crypto/openmako-evidence-court/actions/runs/26836126047", issue_draft)
        self.assertIn("Run status: `Success` for commit `cb1ab5e`", issue_draft)
        self.assertIn("It does not have third-party endorsement from this issue being opened", issue_draft)

        draft_body = issue_draft.split("## Do Not Add Before Posting", 1)[0]
        forbidden = (
            "remote CI is green for `cb1ab5e`",
            "downloaded artifact proves `cb1ab5e`",
            "sent review request",
            "reviewed by",
            "endorsed by",
            "used by",
            "proves tests actually ran",
            "native Claude/Codex/Cursor ingestion",
            "real-world repair accuracy",
            "10k stars achieved",
        )
        safe_text = f"{proof_status}\n{draft_body}"
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                if phrase == "sent review request":
                    self.assertIn("Do not treat this draft as a sent review request", safe_text)
                    continue
                self.assertNotIn(phrase, safe_text)

    def test_launch_assets_keep_v0_1_claims_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        launch_post = (root / "docs" / "LAUNCH_POST.md").read_text(encoding="utf-8")
        social_card = (root / "docs" / "social-card.svg").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("copyable launch post", readme)
        self.assertIn("public proof card", readme)
        self.assertIn("proof status and stale-proof boundary", readme)
        self.assertIn("terminal demo visual", readme)
        self.assertIn("normal-tests comparison", readme)
        self.assertIn("redaction guide", readme)
        self.assertIn("outreach templates", readme)
        self.assertIn("expert review brief", readme)
        self.assertIn("social card", readme)
        self.assertIn("supplied JSON run records", launch_post)
        self.assertIn("explicit marked transcript v0 files", launch_post)
        self.assertIn("explicit Evidence Court JSONL event streams", launch_post)
        self.assertIn("Boundary: this does not ingest native Claude/Codex/Cursor/Devin/CI logs", launch_post)
        self.assertIn("does not prove tests ran outside the supplied record", launch_post)
        self.assertIn("VERDICT: FAIL", social_card)
        self.assertIn("required test not run", social_card)
        self.assertIn("Boundary: not native Claude/Codex/Cursor/Devin/CI log ingestion", social_card)
        forbidden = (
            "native Claude",
            "native Codex",
            "broad SWE",
            "Desktop L4",
            "quant trading ready",
            "proves tests ran",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                if phrase == "native Claude":
                    self.assertIn("does not ingest native Claude", launch_post)
                    continue
                self.assertNotIn(phrase, launch_post)
                self.assertNotIn(phrase, social_card)

    def test_expert_review_brief_keeps_share_claims_verifiable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        brief = (root / "docs" / "EXPERT_REVIEW_BRIEF.md").read_text(encoding="utf-8")
        release_notes = (root / "docs" / "RELEASE_NOTES_V0_1_1.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("30-Second Check", brief)
        self.assertIn("mako evidence-court --demo bad-run", brief)
        self.assertIn("Verdict: FAIL", brief)
        self.assertIn("Safe Quote", brief)
        self.assertIn("examples/evidence-court/bad-run.report.json", brief)
        self.assertIn("diff -u examples/evidence-court/bad-run.report.json -", brief)
        self.assertIn("should produce no diff", brief)
        self.assertIn("Do Not Share If", brief)
        self.assertIn("GitHub Actions smoke gate is red", brief)
        self.assertIn("full JSON report fixture no longer matches", brief)
        self.assertIn("native Claude/Codex/Cursor/Devin/CI log ingestion is supported", brief)
        self.assertIn("does not provide proof that tests actually ran outside", brief)
        self.assertIn("expert review brief", readme)
        self.assertIn("v0.1.2 release notes", readme)
        self.assertIn("public review assets", release_notes)
        self.assertIn("Not Claimed", release_notes)

        forbidden = (
            "10k stars",
            "10000 stars",
            "native Claude ingestion is supported",
            "proves tests actually ran",
            "autonomous repair capability is proven",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, brief)
                self.assertNotIn(phrase, release_notes)

    def test_outreach_templates_are_review_first_and_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        outreach = (root / "docs" / "OUTREACH.md").read_text(encoding="utf-8")
        release_notes = (root / "docs" / "RELEASE_NOTES_V0_1_2.md").read_text(encoding="utf-8")
        launch_post = (root / "docs" / "LAUNCH_POST.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        issue_template = (
            root / ".github" / "ISSUE_TEMPLATE" / "technical-review-request.md"
        ).read_text(encoding="utf-8")

        self.assertIn("review-first outreach templates", release_notes)
        self.assertIn("v0.1.2 release notes", readme)
        self.assertIn("outreach templates", readme)
        self.assertIn("technical review request", readme)
        self.assertIn("technical-review-request.md", readme)
        self.assertIn("Star this if you want a tiny CI-friendly gate", readme)
        self.assertIn("claiming \"tests passed\" without supplied evidence", readme)
        self.assertIn("Not claimed: native", readme)
        self.assertIn("issues/new?template=technical-review-request.md", outreach)
        self.assertIn("TECHNICAL_REVIEW_REQUEST.md", outreach)
        self.assertIn("technical boundary feedback", release_notes)
        self.assertIn("Reference green smoke run", outreach)
        self.assertIn("actions/runs/26836126047", outreach)
        self.assertIn("Reference smoke artifact digest", outreach)
        self.assertIn("sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac", outreach)
        self.assertIn("I would value a quick review", outreach)
        self.assertIn("honest enough for", outreach)
        self.assertIn("If you have 30 seconds", outreach)
        self.assertIn("Do Not Say", outreach)
        self.assertIn("does not natively ingest Claude/Codex/Cursor/CI logs", outreach)
        self.assertIn("does not prove tests", outreach)
        self.assertIn("v0.1.2", launch_post)
        self.assertIn("releases/tag/v0.1.2", launch_post)
        for section in (
            "General AI Tooling Maintainer",
            "Agent Framework Author",
            "CI / DevTools Engineer",
            "Researcher / Evaluator",
            "Short Public Post",
        ):
            with self.subTest(section=section):
                self.assertIn(section, outreach)

        forbidden = (
            "endorsed the project",
            "uses the project",
            "10k stars achieved",
            "10000 stars",
            "native Claude ingestion is supported",
            "proves tests actually ran",
            "autonomous repair capability is proven",
            "please retweet",
            "guaranteed",
            "Reviewed green smoke",
            "honest enough to share",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, outreach)
                self.assertNotIn(phrase, release_notes)
                self.assertNotIn(phrase, issue_template)

    def test_technical_review_request_is_bounded_and_actionable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        review = (root / "docs" / "TECHNICAL_REVIEW_REQUEST.md").read_text(encoding="utf-8")
        outreach = (root / "docs" / "OUTREACH.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        issue_template = (
            root / ".github" / "ISSUE_TEMPLATE" / "technical-review-request.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Technical Review Request", review)
        self.assertIn("public request for technical review", review)
        self.assertIn("not asking for endorsement or", review)
        self.assertIn("Review Questions", review)
        self.assertIn("Evidence Links", review)
        self.assertIn("Quick Local Check", review)
        self.assertIn("Machine-Readable Report Check", review)
        self.assertIn("Boundaries", review)
        self.assertIn("How To Respond", review)
        self.assertIn("does not prove tests actually ran outside the supplied record", review)
        self.assertIn("does not natively ingest Claude/Codex/Cursor/Devin/CI logs", review)
        self.assertIn("docs/TECHNICAL_REVIEW_REQUEST.md", readme)
        self.assertIn("Technical review request", issue_template)
        self.assertIn("not an endorsement request", issue_template)
        self.assertIn("not evidence that anyone has reviewed", issue_template)
        self.assertIn("only creates a public request URL", issue_template)
        self.assertIn("not `replied` or", issue_template)

        questions = re.findall(r"^\d+\. ", review, flags=re.MULTILINE)
        self.assertEqual(len(questions), 3)
        template_questions = re.findall(r"^\d+\. ", issue_template, flags=re.MULTILINE)
        self.assertEqual(len(template_questions), 3)
        review_runs = re.findall(r"actions/runs/(\d+)", review)
        outreach_runs = re.findall(r"actions/runs/(\d+)", outreach)
        template_runs = re.findall(r"actions/runs/(\d+)", issue_template)
        self.assertEqual(set(review_runs), set(outreach_runs))
        self.assertEqual(set(review_runs), set(template_runs))
        review_digests = re.findall(r"sha256:[0-9a-f]{64}", review)
        outreach_digests = re.findall(r"sha256:[0-9a-f]{64}", outreach)
        template_digests = re.findall(r"sha256:[0-9a-f]{64}", issue_template)
        self.assertEqual(set(review_digests), set(outreach_digests))
        self.assertEqual(set(review_digests), set(template_digests))
        for phrase in (
            "https://github.com/1966536805l-crypto/openmako-evidence-court",
            "https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/PUBLIC_PROOF.md",
            "https://github.com/1966536805l-crypto/openmako-evidence-court/blob/main/docs/demo-terminal.svg",
            "actions/runs/26836126047",
            "sha256:7ec4b7b76b0486ebad593e2936bd083ab80e0eee65c628c80f4ea64852095eac",
            "mako evidence-court --demo bad-run",
            "mako evidence-court --input examples/evidence-court/bad-run.json --json | diff -u examples/evidence-court/bad-run.report.json -",
            "examples/evidence-court/bad-run.report.json",
            '"schema_version": "evidence-court.report.v0.1"',
            '"verdict": "FAIL"',
            "test output status reason: no known pass/fail pattern matched",
            "Verdict: FAIL",
            "docs/OUTREACH_TARGETS.md",
            "not valid",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, review)

        forbidden = (
            "please retweet",
            "10k",
            "10000",
            "guaranteed",
            "native Claude ingestion is supported",
            "native Codex ingestion is supported",
            "endorsed by",
            "reviewed by",
            "adopted by",
            "shared by",
        )
        normalized = review.lower()
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase.lower(), normalized)

    def test_outreach_targets_are_candidates_and_bounded(self) -> None:
        root = Path(__file__).resolve().parents[1]
        targets = (root / "docs" / "OUTREACH_TARGETS.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("outreach target tracker", readme)
        self.assertIn("None of these people, projects, or organizations has endorsed", targets)
        self.assertIn("This file is not evidence of interest, adoption, endorsement, review, or sharing.", targets)
        self.assertIn("Do not imply endorsement, partnership, usage, or affiliation.", targets)
        self.assertIn("One polite message per target. No follow-up unless they reply.", targets)
        self.assertIn("Target publicly shared; requires a public share URL", targets)
        self.assertIn("Start with five targets before scaling", targets)
        self.assertIn("Recommended Send Order", targets)
        self.assertIn("future concrete technical review", targets)
        self.assertIn("Trend-Watch Targets", targets)
        self.assertIn("current reason-code branch has public PR-head CI", targets)
        self.assertIn("Hermes Agent", targets)
        self.assertIn("OpenClaw", targets)
        self.assertIn("opencode", targets)
        self.assertIn("Highest potential evaluation relevance", targets)
        self.assertIn("Do Not Say", targets)

        for status in ("candidate", "drafted", "sent", "replied", "shared", "closed"):
            with self.subTest(status=status):
                self.assertIn(f"`{status}`", targets)

        target_list = targets.split("## Target List", maxsplit=1)[1].split("## First Batch", maxsplit=1)[0]
        target_rows = re.findall(
            r"^\| \d+ \| (?P<target>.+?) \| .+? \| (?P<status>candidate|sent) \|$",
            target_list,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(target_rows), 23)
        self.assertEqual(
            [target for target, status in target_rows if status == "sent"],
            ["SWE-agent / mini-SWE-agent", "SWE-bench"],
        )
        self.assertEqual(len([status for _, status in target_rows if status == "candidate"]), 21)

        urls = re.findall(r"`(https://[^`]+)`", target_list)
        self.assertEqual(len(urls), 23)
        for url in urls:
            with self.subTest(url=url):
                self.assertNotIn(" ", url)
                self.assertTrue(url.startswith("https://"))

        for first_batch_target in (
            "OpenHands",
            "SWE-agent / mini-SWE-agent",
            "Aider",
            "LangGraph",
            "SWE-bench",
        ):
            with self.subTest(first_batch_target=first_batch_target):
                self.assertIn(first_batch_target, targets)

        trend_watch = targets.split("## Trend-Watch Targets", maxsplit=1)[1].split(
            "## First-Batch Contact URLs",
            maxsplit=1,
        )[0]
        for phrase in (
            "Hermes Agent",
            "OpenClaw",
            "opencode",
            "high-reach local-agent",
            "does not ingest Hermes/OpenClaw native logs",
            "--fail-on-reason-code test.required_not_run",
            "No affiliation, adoption, integration, or sandbox proof is claimed.",
        ):
            with self.subTest(trend_watch_phrase=phrase):
                self.assertIn(phrase, trend_watch)

        tracker = targets.split("## Tracking Fields To Fill After Sending", maxsplit=1)[1].split(
            "## Do Not Say", maxsplit=1
        )[0]
        for issue_url in (
            "https://github.com/SWE-agent/mini-swe-agent/issues/848",
            "https://github.com/SWE-bench/SWE-bench/issues/595",
        ):
            with self.subTest(issue_url=issue_url):
                self.assertIn(issue_url, tracker)
                self.assertIn("Public issue opened; no reply yet.", tracker)

        self.assertLess(
            targets.index("| 1 | SWE-agent / mini-SWE-agent |"),
            targets.index("| 2 | Aider |"),
        )

        before_do_not_say, do_not_say = targets.split("## Do Not Say", maxsplit=1)
        self.assertIn("Evidence Court proves tests actually ran outside the supplied record.", do_not_say)
        forbidden = (
            "endorsed the project",
            "uses the project",
            "10k stars",
            "10000 stars",
            "native Claude ingestion is supported",
            "proves tests actually ran",
            "autonomous repair capability is proven",
            "please retweet",
            "guaranteed",
            "Reviewed green smoke",
            "already reviewed",
            "one tighter technical review",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, before_do_not_say)

    def test_immediate_send_packet_is_two_short_review_first_messages(self) -> None:
        root = Path(__file__).resolve().parents[1]
        targets = (root / "docs" / "OUTREACH_TARGETS.md").read_text(encoding="utf-8")

        self.assertIn("## Immediate Send Packet", targets)
        packet = targets.split("## Immediate Send Packet", maxsplit=1)[1].split("## First-Batch Send Drafts", maxsplit=1)[0]
        messages = re.findall(
            r"^### \d+\. (SWE-agent / mini-SWE-agent|Aider)\n\n```text\n(.+?)\n```",
            packet,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertEqual([name for name, _ in messages], ["SWE-agent / mini-SWE-agent", "Aider"])

        required = (
            "https://github.com/1966536805l-crypto/openmako-evidence-court",
            "docs/technical_review_request.md",
            "not asking",
            "technical boundary feedback",
        )
        forbidden = (
            "please retweet",
            "retweet",
            "10k",
            "10000",
            "guaranteed",
            "native ingestion",
            "native claude",
            "native codex",
            "native cursor",
            "native ci",
        )
        for name, message in messages:
            with self.subTest(name=name):
                normalized = " ".join(message.lower().split())
                self.assertLessEqual(len(message.split()), 80)
                for phrase in required:
                    self.assertIn(phrase.lower(), normalized)
                for phrase in forbidden:
                    self.assertNotIn(phrase, normalized)

    def test_first_batch_send_drafts_are_specific_and_review_first(self) -> None:
        root = Path(__file__).resolve().parents[1]
        targets = (root / "docs" / "OUTREACH_TARGETS.md").read_text(encoding="utf-8")

        for section in (
            "First-Batch Contact URLs",
            "First-Batch Specific Asks",
            "Immediate Send Packet",
            "First-Batch Send Drafts",
            "Tracking Fields To Fill After Sending",
        ):
            with self.subTest(section=section):
                self.assertIn(f"## {section}", targets)

        first_batch = (
            "OpenHands",
            "SWE-agent / mini-SWE-agent",
            "Aider",
            "LangGraph",
            "SWE-bench",
        )
        contact_section = targets.split("## First-Batch Contact URLs", maxsplit=1)[1].split(
            "## First-Batch Specific Asks",
            maxsplit=1,
        )[0]
        ask_section = targets.split("## First-Batch Specific Asks", maxsplit=1)[1].split(
            "## First-Batch Send Drafts",
            maxsplit=1,
        )[0]
        for name in first_batch:
            with self.subTest(name=name):
                self.assertIsNotNone(
                    re.search(
                        rf"^\| {re.escape(name)} \| `https://[^`]+` \| .+ \| .+ \|$",
                        contact_section,
                        flags=re.MULTILINE,
                    ),
                    msg=f"missing contact URL row for {name}",
                )
                self.assertIsNotNone(
                    re.search(
                        rf"^\| {re.escape(name)} \| .+ \| .+ \| .+ \|$",
                        ask_section,
                        flags=re.MULTILINE,
                    ),
                    msg=f"missing specific ask row for {name}",
                )
                self.assertIn(f"### {name}", targets)

        contact_rows = re.findall(r"^\| (.+?) \| `https://[^`]+` \| .+ \| .+ \|$", contact_section, flags=re.MULTILINE)
        self.assertEqual(set(contact_rows), set(first_batch))

        for phrase in (
            "quick technical review",
            "v0.1.2",
            "docs/PUBLIC_PROOF.md",
            "docs/demo-terminal.svg",
            "Not asking",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, targets)

        draft_section = targets.split("## First-Batch Send Drafts", maxsplit=1)[1].split(
            "## Tracking Fields To Fill After Sending",
            maxsplit=1,
        )[0]
        draft_blocks = re.findall(
            r"^### (.+?)\n\n```text\n(.+?)\n```",
            draft_section,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertEqual(len(draft_blocks), 5)
        for target, draft in draft_blocks:
            with self.subTest(target=target):
                self.assertLessEqual(len(draft.split()), 120)
                normalized = draft.lower()
                self.assertIn("quick technical review", normalized)
                self.assertIn("not asking", normalized)
                self.assertIn("docs/public_proof.md", normalized)
                self.assertIn("docs/demo-terminal.svg", normalized)
                self.assertNotIn("please retweet", normalized)
                self.assertNotIn("10k", normalized)
                self.assertNotIn("guaranteed", normalized)
                self.assertNotIn("native claude", normalized)

        tracking_header = "| Target | Status | Sent date | Contact URL | Message URL | Reply date | Reply URL | Share URL | Message variant | Action needed | Outcome |"
        self.assertIn(tracking_header, targets)

        tracking_section = targets.split("## Tracking Fields To Fill After Sending", maxsplit=1)[1].split(
            "## Do Not Say",
            maxsplit=1,
        )[0]
        tracking_rows = re.findall(
            r"^\| (.+?) \| (.+?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$",
            tracking_section,
            flags=re.MULTILINE,
        )
        rows = [row for row in tracking_rows if row[0] not in {"---", "Target"}]
        self.assertEqual(len(rows), 5)
        tracked_status_by_target = {target.strip(): status.strip() for target, status, *_ in rows}
        tracked_evidence_by_target = {
            target.strip(): {
                "message_url": message_url.strip(),
                "reply_url": reply_url.strip(),
                "share_url": share_url.strip(),
            }
            for target, status, sent_date, contact_url, message_url, reply_date, reply_url, share_url, variant, action, outcome in rows
        }

        target_list = targets.split("## Target List", maxsplit=1)[1].split("## First Batch", maxsplit=1)[0]
        target_rows = re.findall(
            r"^\| \d+ \| (?P<target>.+?) \| .+? \| (?P<status>candidate|drafted|sent|replied|shared|closed) \|$",
            target_list,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(target_rows), 23)
        for target, status in target_rows:
            with self.subTest(target_list_status=target):
                if status != "candidate":
                    self.assertIn(target, tracked_status_by_target)
                    self.assertEqual(tracked_status_by_target[target], status)

        for target, status, sent_date, contact_url, message_url, reply_date, reply_url, share_url, variant, action, outcome in rows:
            with self.subTest(target=target):
                self.assertIn(status.strip(), {"candidate", "drafted", "sent", "replied", "shared", "closed"})
                self.assertTrue(contact_url.strip().startswith("`https://"))
                if status.strip() in {"sent", "replied", "shared"}:
                    self.assertRegex(sent_date.strip(), r"^2026-\d{2}-\d{2}$")
                    self.assertTrue(message_url.strip().startswith("`https://"))
                    self._assert_not_self_hosted_third_party_evidence_url(message_url)
                if status.strip() in {"replied", "shared"}:
                    self.assertRegex(reply_date.strip(), r"^2026-\d{2}-\d{2}$")
                    self.assertTrue(reply_url.strip().startswith("`https://"))
                    self._assert_not_self_hosted_third_party_evidence_url(reply_url)
                if status.strip() == "shared":
                    self.assertTrue(share_url.strip().startswith("`https://"))
                    self._assert_not_self_hosted_third_party_evidence_url(share_url)
        for target, status in tracked_status_by_target.items():
            with self.subTest(tracked_target_status=target):
                if status in {"sent", "replied", "shared"}:
                    self.assertTrue(tracked_evidence_by_target[target]["message_url"].startswith("`https://"))
                if status in {"replied", "shared"}:
                    self.assertTrue(tracked_evidence_by_target[target]["reply_url"].startswith("`https://"))
                if status == "shared":
                    self.assertTrue(tracked_evidence_by_target[target]["share_url"].startswith("`https://"))

    def test_terminal_demo_visual_stays_bounded_and_renderable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        visual_path = root / "docs" / "demo-terminal.svg"
        visual = visual_path.read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        tree = ET.parse(visual_path)
        root_node = tree.getroot()
        self.assertTrue(root_node.tag.endswith("svg"))
        for element in root_node.iter():
            self.assertFalse(element.tag.endswith("script"))
            self.assertFalse(element.tag.endswith("foreignObject"))
            for attribute, value in element.attrib.items():
                self.assertFalse(attribute.lower().startswith("on"))
                self.assertNotIn("http://", value)
                self.assertNotIn("https://", value)
        self.assertIn("![OpenMako Evidence Court bad-run demo](docs/demo-terminal.svg)", readme)
        self.assertLess(readme.index("docs/demo-terminal.svg"), readme.index("## 10-Second Demo"))
        self.assertIn("mako evidence-court --demo bad-run", visual)
        self.assertIn("Claim", visual)
        self.assertIn("Evidence", visual)
        self.assertIn("Verdict", visual)
        self.assertIn("FAIL", visual)
        self.assertIn("supplied run records only", visual)
        self.assertIn("not native Claude/Codex/Cursor/Devin/CI log ingestion", visual)
        self.assertIn("Does not prove tests ran outside the supplied record", visual)

        forbidden = (
            "native Claude ingestion is supported",
            "proves tests actually ran",
            "broad SWE",
            "Desktop L4",
            "quant trading ready",
            "10k stars",
            "10000 stars",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, visual)

    def test_public_proof_card_binds_claim_to_remote_evidence(self) -> None:
        root = Path(__file__).resolve().parents[1]
        proof = (root / "docs" / "PUBLIC_PROOF.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("Safe Public Claim", proof)
        self.assertIn("Evidence Anchor", proof)
        self.assertIn("Artifact Review Path", proof)
        self.assertIn("v0.1.2", proof)
        self.assertIn("e00cf35a92c09f81ab5cff4169d0dc55fd071811", proof)
        self.assertIn("actions/runs/26831075226", proof)
        self.assertIn("completed successfully", proof)
        self.assertIn("evidence-court-smoke", proof)
        self.assertIn("sha256:0f1df42566dbc2352733e3b219117471e0299de3d8004635e265ccd4e9543205", proof)
        self.assertIn("artifact-manifest.json", proof)
        self.assertIn("reviewer-quickstart.md", proof)
        self.assertIn("bad-run.md", proof)
        self.assertIn("good-run.json", proof)
        self.assertIn("marked-transcript.json", proof)
        self.assertIn("mixed-source-rejection.txt", proof)
        self.assertIn("smoke-summary.txt", proof)
        self.assertIn("public page proves artifact metadata", proof)
        self.assertIn("claiming its contents were independently reverified", proof)
        self.assertIn("30-Second Verification", proof)
        self.assertIn("git checkout v0.1.2", proof)
        self.assertIn("mako evidence-court --demo bad-run", proof)
        self.assertIn("Verdict: FAIL", proof)
        self.assertIn("What This Does Not Prove", proof)
        self.assertIn("Native Claude/Codex/Cursor/Devin/CI log ingestion", proof)
        self.assertIn("10k stars, adoption, or endorsement", proof)
        self.assertIn("public proof card", readme)
        self.assertLess(readme.index("Public proof:"), readme.index("## 10-Second Demo"))

        forbidden = (
            "native Claude ingestion is supported",
            "proves tests actually ran",
            "broad SWE repair ability is proven",
            "endorsed by",
            "10000 stars",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, proof)


if __name__ == "__main__":
    unittest.main()
