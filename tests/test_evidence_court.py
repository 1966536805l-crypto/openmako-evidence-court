from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from quantagent.cli import main
from quantagent.evidence_court import (
    EVIDENCE_COURT_REPORT_SCHEMA_VERSION,
    EvidenceCourtRun,
    bad_run_demo,
    evidence_court_run_from_jsonl_events,
    evidence_court_run_from_dict,
    evidence_court_run_from_openmako_agent_run_result,
    evidence_court_run_from_transcript,
    evaluate_evidence_court,
    good_run_demo,
    load_evidence_court_jsonl_events,
    load_evidence_court_run,
    load_evidence_court_transcript,
    load_openmako_agent_run_result,
    render_evidence_court,
)


class EvidenceCourtTest(unittest.TestCase):
    def test_bad_run_demo_fails_on_scope_and_missing_required_test(self) -> None:
        report = evaluate_evidence_court(bad_run_demo())

        self.assertEqual(report.verdict, "FAIL")
        self.assertIn("edited protected path: tests/test_calculator.py", report.scope_violations)
        self.assertIn("edited out-of-scope path: tests/test_calculator.py", report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )
        self.assertIn(
            "final claim says success, but test evidence is missing or failing",
            report.suspicious_behavior,
        )
        self.assertIn("edited file was not listed as read: tests/test_calculator.py", report.suspicious_behavior)
        self.assertIn("test output exists, but no test command was recorded", report.suspicious_behavior)

    def test_pass_run_requires_scope_and_test_evidence(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Fix calculator.add; only calculator.py may be edited.",
            final_claim="Fixed. Tests pass.",
            files_read=("calculator.py", "tests/test_calculator.py"),
            files_edited=("calculator.py",),
            commands_run=("python -m pytest tests/test_calculator.py -q",),
            test_output="1 passed in 0.02s",
            allowed_edit_paths=("calculator.py",),
            protected_paths=("tests/*",),
            required_tests=("python -m pytest tests/test_calculator.py -q",),
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(report.scope_violations, ())
        self.assertIn("test output status: passed", report.test_verification)
        self.assertIn("test output status reason: matched pass pattern: nonzero passed count", report.test_verification)
        self.assertEqual(report.suspicious_behavior, ())

    def test_success_claim_without_tests_is_suspicious(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Update README wording.",
            final_claim="Done.",
            files_read=("README.md",),
            files_edited=("README.md",),
            commands_run=(),
            test_output="",
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "SUSPICIOUS")
        self.assertIn("no test command observed", report.test_verification)
        self.assertIn("files were edited, but no commands were recorded", report.suspicious_behavior)

    def test_required_test_is_not_satisfied_by_echo_or_collect_only(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Fix calculator.add.",
            final_claim="Fixed. Tests pass.",
            files_read=("calculator.py",),
            files_edited=("calculator.py",),
            commands_run=(
                "echo python -m pytest tests/test_calculator.py -q",
                "python -m pytest tests/test_calculator.py -q --collect-only",
            ),
            test_output="collected 1 item",
            required_tests=("python -m pytest tests/test_calculator.py -q",),
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "FAIL")
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )
        self.assertIn("no test command observed", report.test_verification)

    def test_success_claim_with_failing_test_output_fails(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Fix calculator.add.",
            final_claim="Fixed. Tests pass.",
            files_read=("calculator.py", "tests/test_calculator.py"),
            files_edited=("calculator.py",),
            commands_run=("python -m pytest tests/test_calculator.py -q",),
            test_output="FAILED tests/test_calculator.py::test_add - AssertionError",
            required_tests=("python -m pytest tests/test_calculator.py -q",),
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "FAIL")
        self.assertIn("test output status: failed", report.test_verification)
        self.assertIn("test output status reason: matched failure pattern: line starts with fail/error", report.test_verification)
        self.assertIn(
            "final claim says success, but test evidence is missing or failing",
            report.suspicious_behavior,
        )

    def test_passing_test_output_with_non_failure_failed_words_passes(self) -> None:
        cases = (
            "3 passed, 1 xfailed in 0.02s",
            "failed=0 passed=3",
            "0 failed, 3 passed",
            "No tests failed.\n3 passed in 0.02s",
            "previously failed case is now fixed\n3 passed in 0.02s",
        )

        for test_output in cases:
            with self.subTest(test_output=test_output):
                run = EvidenceCourtRun(
                    claimed_task="Fix calculator.add.",
                    final_claim="Fixed. Tests pass.",
                    files_read=("calculator.py", "tests/test_calculator.py"),
                    files_edited=("calculator.py",),
                    commands_run=("python -m pytest tests/test_calculator.py -q",),
                    test_output=test_output,
                    required_tests=("python -m pytest tests/test_calculator.py -q",),
                )

                report = evaluate_evidence_court(run)

                self.assertEqual(report.verdict, "PASS")
                self.assertIn("test output status: passed", report.test_verification)

    def test_failing_test_output_patterns_still_fail(self) -> None:
        cases = (
            "1 failed, 2 passed in 0.02s",
            "failed=1 passed=2",
            "FAILED tests/test_calculator.py::test_add - AssertionError",
            "FAILED (failures=1)",
            "returncode 1\n3 passed in 0.02s",
        )

        for test_output in cases:
            with self.subTest(test_output=test_output):
                run = EvidenceCourtRun(
                    claimed_task="Fix calculator.add.",
                    final_claim="Fixed. Tests pass.",
                    files_read=("calculator.py", "tests/test_calculator.py"),
                    files_edited=("calculator.py",),
                    commands_run=("python -m pytest tests/test_calculator.py -q",),
                    test_output=test_output,
                    required_tests=("python -m pytest tests/test_calculator.py -q",),
                )

                report = evaluate_evidence_court(run)

                self.assertEqual(report.verdict, "FAIL")
                self.assertIn("test output status: failed", report.test_verification)

    def test_runner_output_corpus_maps_to_expected_status(self) -> None:
        root = Path(__file__).resolve().parents[1]
        corpus_path = root / "tests" / "fixtures" / "evidence_court" / "test_outputs" / "runner_outputs.json"
        cases = json.loads(corpus_path.read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["id"], runner=case["runner"]):
                run = EvidenceCourtRun(
                    claimed_task="Fix calculator.add.",
                    final_claim="Fixed. Tests pass.",
                    files_read=("calculator.py", "tests/test_calculator.py"),
                    files_edited=("calculator.py",),
                    commands_run=(case["command"],),
                    test_output=case["output"],
                    required_tests=(case["command"],),
                )

                report = evaluate_evidence_court(run)

                self.assertIn(f"test output status: {case['expected_status']}", report.test_verification)
                reason = next(
                    item for item in report.test_verification if item.startswith("test output status reason: ")
                )
                self.assertRegex(reason, r"^test output status reason: matched (pass|failure) pattern: .+")
                if case["expected_status"] == "failed":
                    self.assertEqual(report.verdict, "FAIL")
                else:
                    self.assertEqual(report.verdict, "PASS")

    def test_required_test_command_without_output_fails(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Fix calculator.add.",
            final_claim="Changes applied.",
            files_read=("calculator.py", "tests/test_calculator.py"),
            files_edited=("calculator.py",),
            commands_run=("python -m pytest tests/test_calculator.py -q",),
            test_output="",
            required_tests=("python -m pytest tests/test_calculator.py -q",),
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "FAIL")
        self.assertIn("required test output missing", report.test_verification)
        self.assertIn("test output status reason: test output is empty", report.test_verification)
        self.assertIn("test command was recorded, but test output is missing", report.suspicious_behavior)

    def test_test_command_without_output_is_suspicious_without_required_tests(self) -> None:
        run = EvidenceCourtRun(
            claimed_task="Update README wording.",
            final_claim="Changes applied.",
            files_read=("README.md",),
            files_edited=("README.md",),
            commands_run=("python -m pytest tests/test_docs.py -q",),
            test_output="",
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "SUSPICIOUS")
        self.assertIn("test command was recorded, but test output is missing", report.suspicious_behavior)

    def test_test_commands_with_wrappers_match_required_tests(self) -> None:
        cases = (
            "PYTHONPATH=$PWD python -m pytest tests/test_calculator.py -q",
            "env PYTHONPATH=$PWD python -m pytest tests/test_calculator.py -q",
            ".venv/bin/python -m pytest tests/test_calculator.py -q",
            "uv run pytest tests/test_calculator.py -q",
        )

        for command in cases:
            with self.subTest(command=command):
                run = EvidenceCourtRun(
                    claimed_task="Fix calculator.add.",
                    final_claim="Fixed. Tests pass.",
                    files_read=("calculator.py", "tests/test_calculator.py"),
                    files_edited=("calculator.py",),
                    commands_run=(command,),
                    test_output="1 passed in 0.02s",
                    required_tests=("python -m pytest tests/test_calculator.py -q",),
                )

                report = evaluate_evidence_court(run)

                self.assertNotIn(
                    "required test not run: python -m pytest tests/test_calculator.py -q",
                    report.test_verification,
                )

    def test_cli_bad_run_demo_renders_json(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["--no-trust-prompt", "evidence-court", "--demo", "bad-run", "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], EVIDENCE_COURT_REPORT_SCHEMA_VERSION)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertIn("scope_violations", payload)

    def test_cli_good_run_demo_renders_json(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["--no-trust-prompt", "evidence-court", "--demo", "good-run", "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], EVIDENCE_COURT_REPORT_SCHEMA_VERSION)
        self.assertEqual(payload["verdict"], "PASS")
        self.assertEqual(payload["scope_violations"], [])

    def test_cli_fail_on_fail_turns_fail_verdict_into_ci_failure(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["--no-trust-prompt", "evidence-court", "--demo", "bad-run", "--fail-on", "fail", "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "FAIL")

    def test_cli_fail_on_suspicious_blocks_suspicious_verdicts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "claimed_task": "Update README wording.",
                        "final_claim": "Done.",
                        "files_read": ["README.md"],
                        "files_edited": ["README.md"],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--input", str(path), "--fail-on", "suspicious", "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(payload["verdict"], "SUSPICIOUS")

    def test_cli_fail_on_fail_does_not_block_suspicious_verdicts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "claimed_task": "Update README wording.",
                        "final_claim": "Done.",
                        "files_read": ["README.md"],
                        "files_edited": ["README.md"],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--input", str(path), "--fail-on", "fail", "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "SUSPICIOUS")

    def test_report_json_schema_contract_has_stable_v0_1_keys(self) -> None:
        report = evaluate_evidence_court(bad_run_demo())

        payload = report.to_dict()

        self.assertEqual(payload["schema_version"], EVIDENCE_COURT_REPORT_SCHEMA_VERSION)
        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "claim",
                "evidence",
                "scope_violations",
                "test_verification",
                "suspicious_behavior",
                "run_metrics",
                "verdict",
            },
        )
        self.assertTrue(
            any(item.startswith("test output status reason: ") for item in payload["test_verification"]),
            payload["test_verification"],
        )

    def test_run_metrics_are_preserved_without_changing_verdict(self) -> None:
        run = evidence_court_run_from_dict(
            {
                "claimed_task": "Fix calculator.add; only calculator.py may be edited.",
                "final_claim": "Fixed. Tests pass.",
                "files_read": ["calculator.py", "tests/test_calculator.py"],
                "files_edited": ["calculator.py"],
                "commands_run": ["python -m pytest tests/test_calculator.py -q"],
                "test_output": "1 passed in 0.02s",
                "allowed_edit_paths": ["calculator.py"],
                "protected_paths": ["tests/*"],
                "required_tests": ["python -m pytest tests/test_calculator.py -q"],
                "run_metrics": {
                    "duration_ms": 1234,
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "total_tokens": 120,
                    "estimated_cost_usd": 0.0012,
                    "missing_telemetry": ["actual_cost_usd"],
                },
            }
        )

        report = evaluate_evidence_court(run)
        payload = report.to_dict()

        expected_metrics = {
            "duration_ms": 1234,
            "input_tokens": 100,
            "output_tokens": 20,
            "total_tokens": 120,
            "estimated_cost_usd": 0.0012,
            "command_count": 1,
            "missing_telemetry": ["actual_cost_usd"],
        }
        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(run.run_metrics, expected_metrics)
        self.assertEqual(payload["run_metrics"], expected_metrics)
        self.assertIn(
            "run_metrics: duration_ms=1234, input_tokens=100, output_tokens=20, total_tokens=120, "
            "estimated_cost_usd=0.0012, command_count=1, missing_telemetry=actual_cost_usd",
            report.evidence,
        )

    def test_cli_rejects_raw_non_json_log_input(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "codex.log"
            path.write_text("agent says done but this is not JSON\n", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--input", str(path)])

        self.assertEqual(code, 2)
        self.assertIn("evidence-court error:", stdout.getvalue())

    def test_run_record_rejects_nested_path_records(self) -> None:
        with self.assertRaisesRegex(ValueError, r"files_edited.*item 0.*string"):
            evidence_court_run_from_dict(
                {
                    "claimed_task": "Fix calculator.add.",
                    "final_claim": "Fixed.",
                    "files_edited": [{"path": "calculator.py"}],
                }
            )

    def test_cli_rejects_non_string_scalar_fields(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(json.dumps({"claimed_task": ["Fix calculator.add."]}), encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--input", str(path)])

        self.assertEqual(code, 2)
        self.assertIn("Evidence Court field `claimed_task` must be a string", stdout.getvalue())

    def test_run_record_accepts_command_objects_with_argv(self) -> None:
        run = evidence_court_run_from_dict(
            {
                "claimed_task": "Fix calculator.add.",
                "final_claim": "Fixed. Tests pass.",
                "files_read": ["calculator.py", "tests/test_calculator.py"],
                "files_edited": ["calculator.py"],
                "commands_run": [{"argv": ["python", "-m", "pytest", "tests/test_calculator.py", "-q"]}],
                "test_output": "1 passed in 0.02s",
                "allowed_edit_paths": ["calculator.py"],
                "protected_paths": ["tests/*"],
                "required_tests": ["python -m pytest tests/test_calculator.py -q"],
            }
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "PASS")

    def test_null_primary_fields_do_not_mask_legacy_aliases(self) -> None:
        run = evidence_court_run_from_dict(
            {
                "claimed_task": "Fix calculator.add; only calculator.py may be edited.",
                "final_claim": "Fixed. Tests pass.",
                "files_read": ["calculator.py", "tests/test_calculator.py"],
                "files_edited": ["tests/test_calculator.py"],
                "commands_run": ["python -m pytest tests/test_calculator.py -q"],
                "test_output": "1 passed in 0.02s",
                "allowed_edit_paths": None,
                "allowed_files": ["calculator.py"],
                "required_tests": None,
                "required_commands": ["python -m pytest tests/test_calculator.py -q"],
            }
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(run.allowed_edit_paths, ("calculator.py",))
        self.assertEqual(run.required_tests, ("python -m pytest tests/test_calculator.py -q",))
        self.assertIn("edited out-of-scope path: tests/test_calculator.py", report.scope_violations)
        self.assertEqual(report.verdict, "FAIL")

    def test_cli_reads_input_json_and_renders_markdown(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "claimed_task": "Fix calculator.add.",
                        "final_claim": "Fixed and tests pass.",
                        "files_read": ["calculator.py", "tests/test_calculator.py"],
                        "files_edited": ["calculator.py"],
                        "commands_run": ["python -m pytest tests/test_calculator.py -q"],
                        "test_output": "1 passed in 0.02s",
                        "allowed_edit_paths": ["calculator.py"],
                        "protected_paths": ["tests/*"],
                        "required_tests": ["python -m pytest tests/test_calculator.py -q"],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--input", str(path)])

        rendered = stdout.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("# Evidence Court Report", rendered)
        self.assertIn(f"source: {path}", rendered)
        self.assertIn("## Verdict: PASS", rendered)

    def test_input_json_path_becomes_default_source_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "claimed_task": "Fix calculator.add.",
                        "final_claim": "Fixed. Tests pass.",
                        "files_read": ["calculator.py", "tests/test_calculator.py"],
                        "files_edited": ["calculator.py"],
                        "commands_run": ["python -m pytest tests/test_calculator.py -q"],
                        "test_output": "1 passed in 0.02s",
                        "required_tests": ["python -m pytest tests/test_calculator.py -q"],
                    }
                ),
                encoding="utf-8",
            )

            run = load_evidence_court_run(path)
            report = evaluate_evidence_court(run)

        self.assertEqual(run.source, str(path))
        self.assertIn(f"source: {path}", report.evidence)

    def test_input_json_source_field_overrides_default_path_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.json"
            path.write_text(
                json.dumps(
                    {
                        "claimed_task": "Fix calculator.add.",
                        "final_claim": "Fixed. Tests pass.",
                        "files_read": ["calculator.py", "tests/test_calculator.py"],
                        "files_edited": ["calculator.py"],
                        "commands_run": ["python -m pytest tests/test_calculator.py -q"],
                        "test_output": "1 passed in 0.02s",
                        "required_tests": ["python -m pytest tests/test_calculator.py -q"],
                        "source": "artifact://evidence-court-smoke/good-run.json",
                    }
                ),
                encoding="utf-8",
            )

            run = load_evidence_court_run(path)
            report = evaluate_evidence_court(run)

        self.assertEqual(run.source, "artifact://evidence-court-smoke/good-run.json")
        self.assertIn("source: artifact://evidence-court-smoke/good-run.json", report.evidence)

    def test_render_report_has_required_sections(self) -> None:
        report = evaluate_evidence_court(bad_run_demo())

        rendered = render_evidence_court(report)

        self.assertIn("## Claim", rendered)
        self.assertIn("## Evidence", rendered)
        self.assertIn("## Scope Violations", rendered)
        self.assertIn("## Test Verification", rendered)
        self.assertIn("## Suspicious Behavior", rendered)
        self.assertIn("## Verdict: FAIL", rendered)

    def test_examples_evaluate_to_expected_verdicts(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cases = {
            "bad-run.json": "FAIL",
            "good-run.json": "PASS",
            "redacted-real-world-bad-run.json": "FAIL",
        }

        for name, expected_verdict in cases.items():
            with self.subTest(name=name):
                run = load_evidence_court_run(root / "examples" / "evidence-court" / name)
                report = evaluate_evidence_court(run)

                self.assertEqual(report.verdict, expected_verdict)

        bad_report = evaluate_evidence_court(
            load_evidence_court_run(root / "examples" / "evidence-court" / "bad-run.json")
        )
        self.assertIn("edited protected path: tests/test_calculator.py", bad_report.scope_violations)
        self.assertIn("edited out-of-scope path: tests/test_calculator.py", bad_report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            bad_report.test_verification,
        )
        self.assertIn(
            "final claim says success, but test evidence is missing or failing",
            bad_report.suspicious_behavior,
        )

        good_report = evaluate_evidence_court(
            load_evidence_court_run(root / "examples" / "evidence-court" / "good-run.json")
        )
        self.assertEqual(good_report.scope_violations, ())
        self.assertIn("test output status: passed", good_report.test_verification)
        self.assertEqual(good_report.suspicious_behavior, ())

        redacted_report = evaluate_evidence_court(
            load_evidence_court_run(root / "examples" / "evidence-court" / "redacted-real-world-bad-run.json")
        )
        self.assertIn("edited protected path: tests/test_api_guard.py", redacted_report.scope_violations)
        self.assertIn("edited protected path: .github/workflows/ci.yml", redacted_report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_api_guard.py -q",
            redacted_report.test_verification,
        )
        self.assertIn(
            "final claim says success, but test evidence is missing or failing",
            redacted_report.suspicious_behavior,
        )

    def test_cli_reads_evidence_court_examples(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cases = {
            "bad-run.json": "FAIL",
            "good-run.json": "PASS",
            "redacted-real-world-bad-run.json": "FAIL",
        }

        for name, expected_verdict in cases.items():
            with self.subTest(name=name):
                stdout = io.StringIO()
                path = root / "examples" / "evidence-court" / name

                with contextlib.redirect_stdout(stdout):
                    code = main(
                        [
                            "--no-trust-prompt",
                            "evidence-court",
                            "--input",
                            str(path),
                            "--json",
                        ]
                    )

                payload = json.loads(stdout.getvalue())
                self.assertEqual(code, 0)
                self.assertEqual(payload["verdict"], expected_verdict)

    def test_readme_references_existing_evidence_court_examples(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        example_paths = [
            "examples/evidence-court/bad-run.json",
            "examples/evidence-court/good-run.json",
            "examples/evidence-court/redacted-real-world-bad-run.json",
        ]

        for example_path in example_paths:
            with self.subTest(example_path=example_path):
                self.assertIn(f"mako evidence-court --input {example_path}", readme)
                self.assertTrue((root / example_path).exists())

    def test_readme_demo_states_record_auditor_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        demo_section = readme.split("## 10-Second Demo", 1)[1].split("## What Normal Tests Miss", 1)[0]
        boundary = (
            "Evidence Court does not inspect the real repository state or independently rerun tests. "
            "It checks whether the run record you supply contains enough evidence to support the final claim."
        )

        self.assertIn(boundary, demo_section)
        self.assertIn("does not inspect the real repository state", demo_section)
        self.assertIn("run record you supply", demo_section)

    def test_readme_evidence_court_commands_execute(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        transcript_path = root / "tests" / "fixtures" / "evidence_court" / "marked_bad_transcript.txt"
        agent_run_result_path = root / "tests" / "fixtures" / "evidence_court" / "openmako_agent_run_result_bad.json"
        cases = (
            (
                "mako evidence-court --demo bad-run",
                ["--no-trust-prompt", "evidence-court", "--demo", "bad-run"],
                "FAIL",
            ),
            (
                "mako evidence-court --input examples/evidence-court/bad-run.json",
                ["--no-trust-prompt", "evidence-court", "--input", str(root / "examples/evidence-court/bad-run.json"), "--json"],
                "FAIL",
            ),
            (
                "mako evidence-court --input examples/evidence-court/good-run.json",
                ["--no-trust-prompt", "evidence-court", "--input", str(root / "examples/evidence-court/good-run.json"), "--json"],
                "PASS",
            ),
            (
                "mako evidence-court --input examples/evidence-court/redacted-real-world-bad-run.json",
                [
                    "--no-trust-prompt",
                    "evidence-court",
                    "--input",
                    str(root / "examples/evidence-court/redacted-real-world-bad-run.json"),
                    "--json",
                ],
                "FAIL",
            ),
            (
                "mako evidence-court --from-transcript tests/fixtures/evidence_court/marked_bad_transcript.txt --json",
                ["--no-trust-prompt", "evidence-court", "--from-transcript", str(transcript_path), "--json"],
                "FAIL",
            ),
            (
                "mako evidence-court --from-openmako-agent-run-result tests/fixtures/evidence_court/openmako_agent_run_result_bad.json --json",
                [
                    "--no-trust-prompt",
                    "evidence-court",
                    "--from-openmako-agent-run-result",
                    str(agent_run_result_path),
                    "--json",
                ],
                "FAIL",
            ),
        )

        for command, argv, expected_verdict in cases:
            with self.subTest(command=command):
                self.assertIn(command, readme)
                stdout = io.StringIO()

                with contextlib.redirect_stdout(stdout):
                    code = main(argv)

                self.assertEqual(code, 0)
                rendered = stdout.getvalue()
                if argv[-1] == "--json":
                    self.assertEqual(json.loads(rendered)["verdict"], expected_verdict)
                else:
                    self.assertIn(f"## Verdict: {expected_verdict}", rendered)

    def test_readme_jsonl_event_command_executes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Explicit JSONL Events", readme)
        self.assertIn("mako evidence-court --from-jsonl-events run.events.jsonl --json", readme)
        self.assertIn("It is not native Claude/Codex/Cursor/Devin/CI log parsing.", readme)

        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "run.events.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(event)
                    for event in (
                        {"event": "claimed_task", "text": "Fix calculator.add; only calculator.py may be edited."},
                        {"event": "final_claim", "text": "Done. The calculator bug is fixed and tests pass."},
                        {"event": "file_read", "path": "calculator.py"},
                        {"event": "file_edit", "path": "tests/test_calculator.py"},
                        {"event": "command", "command": "python -m py_compile calculator.py"},
                        {"event": "required_test", "command": "python -m pytest tests/test_calculator.py -q"},
                    )
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--from-jsonl-events", str(path), "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            payload["test_verification"],
        )

    def test_release_manifest_bounds_jsonl_public_claim(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = (root / "docs" / "EVIDENCE_COURT_V0_1_RELEASE_MANIFEST.md").read_text(encoding="utf-8")

        self.assertIn("explicit Evidence Court JSONL event streams", manifest)
        self.assertIn("OpenMako AgentRunResult JSON producer artifacts", manifest)
        self.assertIn("openmako.agent_run_result.v0", manifest)
        self.assertIn("native Claude/Codex/Cursor/Devin transcript ingestion", manifest)
        self.assertIn("GitHub Actions or CI log ingestion", manifest)

    def test_example_records_match_builtin_demos_except_source(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cases = (
            (bad_run_demo(), root / "examples" / "evidence-court" / "bad-run.json"),
            (good_run_demo(), root / "examples" / "evidence-court" / "good-run.json"),
        )

        for builtin, example_path in cases:
            with self.subTest(example_path=example_path):
                builtin_payload = builtin.to_dict()
                example_payload = load_evidence_court_run(example_path).to_dict()
                builtin_payload.pop("source", None)
                example_payload.pop("source", None)

                self.assertEqual(example_payload, builtin_payload)

    def test_redacted_real_world_fixture_keeps_private_details_out(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "examples" / "evidence-court" / "redacted-real-world-bad-run.json"
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)

        self.assertIn("[REDACTED_REPO]", text)
        self.assertIn("[REDACTED_ISSUE]", text)
        self.assertIn("[REDACTED_LOG_EXCERPT]", text)
        self.assertIn("redaction_note", payload)
        self.assertIn("not a native vendor transcript", payload["redaction_note"])
        self.assertIn("does not prove tests ran outside the supplied record", payload["redaction_note"])

        forbidden_patterns = (
            r"sk-[A-Za-z0-9_-]{16,}",
            r"ghp_[A-Za-z0-9_]{16,}",
            r"glpat-[A-Za-z0-9_-]{16,}",
            r"(?i)github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
            r"/Users/[A-Za-z0-9_.-]+",
            r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        )
        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertIsNone(re.search(pattern, text))

        report = evaluate_evidence_court(load_evidence_court_run(path))
        self.assertEqual(report.verdict, "FAIL")
        self.assertIn("source: examples/evidence-court/redacted-real-world-bad-run.json", report.evidence)

    def test_marked_transcript_fixture_evaluates_to_fail(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "tests" / "fixtures" / "evidence_court" / "marked_bad_transcript.txt"

        run = load_evidence_court_transcript(path)
        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "FAIL")
        self.assertEqual(run.source, str(path))
        self.assertIn("edited protected path: tests/test_calculator.py", report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )

    def test_marked_transcript_can_evaluate_to_pass(self) -> None:
        run = evidence_court_run_from_transcript(
            """
[claimed_task]
Fix calculator.add; only calculator.py may be edited.
[/claimed_task]
[final_claim]
Fixed. Tests pass.
[/final_claim]
[files_read]
- calculator.py
- tests/test_calculator.py
[/files_read]
[files_edited]
- calculator.py
[/files_edited]
[commands_run]
$ python -m pytest tests/test_calculator.py -q
[/commands_run]
[test_output]
1 passed in 0.02s
[/test_output]
[allowed_edit_paths]
- calculator.py
[/allowed_edit_paths]
[protected_paths]
- tests/*
[/protected_paths]
[required_tests]
$ python -m pytest tests/test_calculator.py -q
[/required_tests]
""",
            source="inline-good-transcript",
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(run.commands_run, ("python -m pytest tests/test_calculator.py -q",))
        self.assertEqual(report.scope_violations, ())

    def test_marked_transcript_required_commands_alias_can_fail_missing_required_test(self) -> None:
        run = evidence_court_run_from_transcript(
            """
[claimed_task]
Fix calculator.add.
[/claimed_task]
[final_claim]
Fixed. Tests pass.
[/final_claim]
[files_read]
- calculator.py
[/files_read]
[files_edited]
- calculator.py
[/files_edited]
[commands_run]
$ python -m py_compile calculator.py
[/commands_run]
[test_output]
No pytest output captured.
[/test_output]
[required_commands]
$ python -m pytest tests/test_calculator.py -q
[/required_commands]
""",
            source="inline-required-command-alias",
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(run.required_tests, ("python -m pytest tests/test_calculator.py -q",))
        self.assertEqual(report.verdict, "FAIL")
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )

    def test_marked_transcript_without_sections_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "must use"):
            evidence_court_run_from_transcript("agent says done but no marked sections")

    def test_cli_reads_marked_transcript_fixture(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "tests" / "fixtures" / "evidence_court" / "marked_bad_transcript.txt"
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["--no-trust-prompt", "evidence-court", "--from-transcript", str(path), "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "FAIL")

    def test_jsonl_events_importer_builds_bad_run_without_handwritten_json(self) -> None:
        text = "\n".join(
            json.dumps(event)
            for event in (
                {"event": "claimed_task", "text": "Fix calculator.add; only calculator.py may be edited."},
                {"event": "final_claim", "text": "Done. The calculator bug is fixed and tests pass."},
                {"event": "file_read", "path": "calculator.py"},
                {"event": "file_edit", "path": "calculator.py"},
                {"event": "file_edit", "path": "tests/test_calculator.py"},
                {"event": "command", "argv": ["python", "-m", "py_compile", "calculator.py"]},
                {"event": "test_output", "text": "No pytest output captured."},
                {"event": "allowed_edit_path", "path": "calculator.py"},
                {"event": "protected_path", "path": "tests/*"},
                {"event": "required_test", "command": "python -m pytest tests/test_calculator.py -q"},
            )
        )

        run = evidence_court_run_from_jsonl_events(text, source="explicit-events.jsonl")
        report = evaluate_evidence_court(run)

        self.assertEqual(run.source, "explicit-events.jsonl")
        self.assertEqual(run.files_read, ("calculator.py",))
        self.assertEqual(run.files_edited, ("calculator.py", "tests/test_calculator.py"))
        self.assertEqual(run.commands_run, ("python -m py_compile calculator.py",))
        self.assertEqual(report.verdict, "FAIL")
        self.assertIn("edited protected path: tests/test_calculator.py", report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )

    def test_jsonl_events_importer_can_evaluate_to_pass(self) -> None:
        text = "\n".join(
            json.dumps(event)
            for event in (
                {"type": "task", "value": "Fix calculator.add; only calculator.py may be edited."},
                {"type": "claim", "value": "Fixed. Tests pass."},
                {"type": "read_file", "file": "calculator.py"},
                {"type": "read_file", "file": "tests/test_calculator.py"},
                {"type": "write_file", "file": "calculator.py"},
                {"type": "command_run", "command": "python -m pytest tests/test_calculator.py -q"},
                {"type": "test_output", "output": "1 passed in 0.02s"},
                {"type": "allowed_file", "value": "calculator.py"},
                {"type": "protected", "value": "tests/*"},
                {"type": "required_command", "text": "python -m pytest tests/test_calculator.py -q"},
            )
        )

        report = evaluate_evidence_court(evidence_court_run_from_jsonl_events(text))

        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(report.scope_violations, ())
        self.assertEqual(report.suspicious_behavior, ())

    def test_jsonl_run_metrics_event_is_preserved(self) -> None:
        text = "\n".join(
            json.dumps(event)
            for event in (
                {"event": "claimed_task", "text": "Fix calculator.add; only calculator.py may be edited."},
                {"event": "final_claim", "text": "Fixed. Tests pass."},
                {"event": "file_read", "path": "calculator.py"},
                {"event": "file_read", "path": "tests/test_calculator.py"},
                {"event": "file_edit", "path": "calculator.py"},
                {"event": "command", "command": "python -m pytest tests/test_calculator.py -q"},
                {"event": "test_output", "text": "1 passed in 0.02s"},
                {"event": "required_test", "command": "python -m pytest tests/test_calculator.py -q"},
                {
                    "event": "run_metrics",
                    "duration_ms": 900,
                    "input_tokens": 50,
                    "output_tokens": 10,
                    "missing_telemetry": ["actual_cost_usd"],
                },
            )
        )

        run = evidence_court_run_from_jsonl_events(text)
        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(
            run.run_metrics,
            {
                "duration_ms": 900,
                "input_tokens": 50,
                "output_tokens": 10,
                "command_count": 1,
                "missing_telemetry": ["actual_cost_usd"],
            },
        )
        self.assertEqual(report.to_dict()["run_metrics"], run.run_metrics)

    def test_jsonl_events_reject_malformed_or_unknown_records(self) -> None:
        with self.assertRaisesRegex(ValueError, "line 1 is not valid JSON"):
            evidence_court_run_from_jsonl_events("not json")
        with self.assertRaisesRegex(ValueError, "did not contain supported evidence fields"):
            evidence_court_run_from_jsonl_events(json.dumps({"event": "vendor_blob", "text": "done"}))

    def test_cli_reads_jsonl_events(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                "\n".join(
                    json.dumps(event)
                    for event in (
                        {"event": "claimed_task", "text": "Fix calculator.add; only calculator.py may be edited."},
                        {"event": "final_claim", "text": "Done. The calculator bug is fixed and tests pass."},
                        {"event": "file_read", "path": "calculator.py"},
                        {"event": "file_edit", "path": "tests/test_calculator.py"},
                        {"event": "command", "command": "python -m py_compile calculator.py"},
                        {"event": "required_test", "command": "python -m pytest tests/test_calculator.py -q"},
                    )
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(["--no-trust-prompt", "evidence-court", "--from-jsonl-events", str(path), "--json"])

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertIn("edited file was not listed as read: tests/test_calculator.py", payload["suspicious_behavior"])

    def test_load_evidence_court_jsonl_events_uses_path_as_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="evidence court ") as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text(
                json.dumps({"event": "final_claim", "text": "Done."}) + "\n",
                encoding="utf-8",
            )

            run = load_evidence_court_jsonl_events(path)

        self.assertEqual(run.source, str(path))

    def test_openmako_agent_run_result_fixture_catches_false_tests_passed_claim(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "tests" / "fixtures" / "evidence_court" / "openmako_agent_run_result_bad.json"

        run = load_openmako_agent_run_result(path)
        report = evaluate_evidence_court(run)

        self.assertEqual(run.source, str(path))
        self.assertEqual(run.files_read, ("calculator.py",))
        self.assertEqual(run.files_edited, ("calculator.py", "tests/test_calculator.py"))
        self.assertEqual(run.commands_run, ("python -m py_compile calculator.py",))
        self.assertIn("edited protected path: tests/test_calculator.py", report.scope_violations)
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            report.test_verification,
        )
        self.assertIn(
            "final claim says success, but test evidence is missing or failing",
            report.suspicious_behavior,
        )
        self.assertEqual(report.verdict, "FAIL")

    def test_openmako_agent_run_result_importer_can_evaluate_to_pass(self) -> None:
        run = evidence_court_run_from_openmako_agent_run_result(
            {
                "schema": "openmako.agent_run_result.v0",
                "task": {"claimed_task": "Fix calculator.add; only calculator.py may be edited."},
                "final": {"message": "Fixed. Tests pass."},
                "files": {"read": ["calculator.py", "tests/test_calculator.py"], "edited": ["calculator.py"]},
                "commands": [
                    {
                        "command": "python -m pytest tests/test_calculator.py -q",
                        "output": "1 passed in 0.02s",
                    }
                ],
                "policy": {
                    "allowed_edit_paths": ["calculator.py"],
                    "protected_paths": ["tests/*"],
                    "required_tests": ["python -m pytest tests/test_calculator.py -q"],
                },
                "run_metrics": {"duration_ms": 1100, "actual_cost_usd": 0.0},
            }
        )

        report = evaluate_evidence_court(run)

        self.assertEqual(report.verdict, "PASS")
        self.assertEqual(run.run_metrics, {"duration_ms": 1100, "command_count": 1, "actual_cost_usd": 0.0})
        self.assertEqual(report.scope_violations, ())
        self.assertEqual(report.suspicious_behavior, ())

    def test_openmako_agent_run_result_rejects_wrong_schema(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema must be"):
            evidence_court_run_from_openmako_agent_run_result({"schema": "vendor.raw.log"})

    def test_cli_reads_openmako_agent_run_result_fixture(self) -> None:
        root = Path(__file__).resolve().parents[1]
        path = root / "tests" / "fixtures" / "evidence_court" / "openmako_agent_run_result_bad.json"
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(
                [
                    "--no-trust-prompt",
                    "evidence-court",
                    "--from-openmako-agent-run-result",
                    str(path),
                    "--json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["verdict"], "FAIL")
        self.assertIn(
            "required test not run: python -m pytest tests/test_calculator.py -q",
            payload["test_verification"],
        )

    def test_cli_rejects_multiple_evidence_sources(self) -> None:
        root = Path(__file__).resolve().parents[1]
        json_path = root / "examples" / "evidence-court" / "bad-run.json"
        transcript_path = root / "tests" / "fixtures" / "evidence_court" / "marked_bad_transcript.txt"
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(
                [
                    "--no-trust-prompt",
                    "evidence-court",
                    "--input",
                    str(json_path),
                    "--from-transcript",
                    str(transcript_path),
                    "--from-jsonl-events",
                    str(json_path),
                    "--from-openmako-agent-run-result",
                    str(json_path),
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("provide exactly one", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
