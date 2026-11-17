import json
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import run_tests_with_ai as ai_runner


def valid_response() -> dict[str, object]:
    return {
        "failure_type": "locator issue",
        "likely_root_cause": "The locator may not identify the expected element.",
        "evidence": ["The supplied failure summary reports a locator timeout."],
        "recommended_fix": "Verify the live DOM before changing the locator.",
        "regression_tests": ["Retain the visibility assertion for the verified locator."],
        "confidence": "Low",
    }


def logged_in_result() -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["codex", "login", "status"],
        returncode=0,
        stdout="Logged in using ChatGPT\n",
        stderr="",
    )


def test_analysis_accepts_schema_valid_codex_response_and_redacts_prompt(monkeypatch):
    response = valid_response()
    calls: list[subprocess.CompletedProcess[str]] = [
        logged_in_result(),
        subprocess.CompletedProcess(
            args=["codex", "exec"],
            returncode=0,
            stdout=json.dumps(response),
            stderr="",
        ),
    ]
    prompts: list[str] = []

    def fake_run(command, **kwargs):
        assert kwargs["timeout"] > 0
        if "login" in command:
            return calls.pop(0)
        assert "--sandbox" in command
        assert command[command.index("--sandbox") + 1] == "read-only"
        prompts.append(kwargs["input"])
        assert kwargs["cwd"] != str(ai_runner.PROJECT_ROOT)
        return calls.pop(0)

    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", fake_run)
    outcome = ai_runner.CodexFailureAnalyzer(timeout_seconds=2).analyze(
        [
            ai_runner.FailureEvidence(
                "test_login.py::test_login",
                "call",
                "AssertionError: password=secret_sauce standard_user",
            )
        ]
    )

    assert outcome.status == "completed"
    assert outcome.response == response
    assert prompts
    assert "secret_sauce" not in prompts[0]
    assert "standard_user" not in prompts[0]
    assert "[REDACTED]" in prompts[0]


def test_malformed_codex_json_is_rejected(monkeypatch):
    calls = [
        logged_in_result(),
        subprocess.CompletedProcess(
            args=["codex", "exec"], returncode=0, stdout="not-json", stderr=""
        ),
    ]
    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", lambda *args, **kwargs: calls.pop(0))

    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "unavailable"
    assert outcome.reason == "Codex response failed JSON/schema/sanitization validation"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value.pop("evidence"),
        lambda value: value.update(confidence=4),
        lambda value: value.update(confidence="Certain"),
        lambda value: value.update(failure_type="unknown category"),
        lambda value: value.update(extra_field="unexpected"),
        lambda value: value.update(regression_tests="not-an-array"),
        lambda value: value.update(evidence=[False]),
    ],
)
def test_schema_rejects_incomplete_wrongly_typed_or_unexpected_response(mutate):
    response = valid_response()
    mutate(response)

    with pytest.raises(ValueError):
        ai_runner.validate_against_schema(response, json.loads(ai_runner.SCHEMA_PATH.read_text()))


def test_missing_codex_cli_is_reported_without_subprocess(monkeypatch):
    run = Mock()
    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: None)
    monkeypatch.setattr(ai_runner.subprocess, "run", run)

    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "unavailable"
    assert outcome.reason == "Codex CLI was not found on PATH"
    run.assert_not_called()


def test_codex_timeout_is_reported(monkeypatch):
    def fake_run(command, **kwargs):
        if "login" in command:
            return logged_in_result()
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", fake_run)

    outcome = ai_runner.CodexFailureAnalyzer(timeout_seconds=1).analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "unavailable"
    assert outcome.reason == "Codex analysis timed out"


def test_unavailable_authentication_prevents_analysis(monkeypatch):
    run = Mock(
        return_value=subprocess.CompletedProcess(
            args=["codex"], returncode=1, stdout="Not logged in", stderr=""
        )
    )
    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", run)

    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "unavailable"
    assert outcome.reason == "Codex CLI authentication is unavailable"
    assert run.call_count == 1


def test_unavailable_provider_does_not_expose_cli_output(monkeypatch):
    calls = [
        logged_in_result(),
        subprocess.CompletedProcess(
            args=["codex", "exec"],
            returncode=17,
            stdout="",
            stderr="private provider detail",
        ),
    ]
    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", lambda *args, **kwargs: calls.pop(0))

    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "unavailable"
    assert "exit code 17" in outcome.reason
    assert "private provider detail" not in outcome.reason


def test_sanitizer_redacts_secrets_and_identifiers_and_skips_ambiguous_input():
    sanitized, reason = ai_runner.sanitize_text(
        "AssertionError: password=secret_sauce Authorization: Bearer token-value "
        "cookie=session-value qa.person@example.com",
        {"secret_sauce", "standard_user", "token-value"},
    )

    assert reason is None
    assert sanitized is not None
    for sensitive in (
        "secret_sauce",
        "standard_user",
        "token-value",
        "qa.person@example.com",
        "session-value",
    ):
        assert sensitive not in sanitized
    assert "[REDACTED]" in sanitized
    quoted, reason = ai_runner.sanitize_text(
        "AssertionError: actual 'private user value' did not match", set()
    )
    assert reason is None
    assert "private user value" not in quoted
    assert "[REDACTED_VALUE]" in quoted

    sanitized, reason = ai_runner.sanitize_text("token=abc\nsecond line", {"secret_sauce"})
    assert sanitized is None
    assert "multi-line" in reason


@pytest.mark.parametrize(
    ("raw", "sensitive_values"),
    [
        ("password=plain-secret", set()),
        ("password is plain-secret", set()),
        ("token=plain-token", set()),
        ("Cookie: session=private-cookie; theme=dark", set()),
        ("Authorization: Bearer private-bearer-token", set()),
        ("Contact user.person@example.test", set()),
        ("Phone 555-123-4567", set()),
    ],
)
def test_sanitizer_never_forwards_common_sensitive_values(raw, sensitive_values):
    sanitized, reason = ai_runner.sanitize_text(raw, sensitive_values)

    assert reason is None
    assert sanitized is not None
    assert "plain-secret" not in sanitized
    assert "plain-token" not in sanitized
    assert "private-cookie" not in sanitized
    assert "private-bearer-token" not in sanitized
    assert "user.person@example.test" not in sanitized
    assert "555-123-4567" not in sanitized


def test_sanitizer_skips_unlabelled_high_entropy_token():
    sanitized, reason = ai_runner.sanitize_text("Unexpected response value A1b2C3d4E5f6G7h8", set())

    assert sanitized is None
    assert "high-entropy" in reason


def test_failure_recording_skips_when_secret_inventory_is_unavailable(monkeypatch):
    monkeypatch.setattr(ai_runner, "collect_sensitive_values", lambda: None)
    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [ai_runner.FailureEvidence("test_login.py::test_login", "call", "AssertionError: mismatch")]
    )

    assert outcome.status == "skipped"
    assert "credential inventory" in outcome.reason


def test_uncertain_evidence_skips_analysis_without_calling_codex(monkeypatch):
    run = Mock()
    monkeypatch.setattr(ai_runner.shutil, "which", lambda _: "/usr/bin/codex")
    monkeypatch.setattr(ai_runner.subprocess, "run", run)

    outcome = ai_runner.CodexFailureAnalyzer().analyze(
        [
            ai_runner.FailureEvidence(
                "test_login.py::test_login",
                "call",
                'AssertionError: {"token": "unknown"}',
            )
        ]
    )

    assert outcome.status == "skipped"
    assert "cannot be sanitized" in outcome.reason
    run.assert_not_called()


def test_normal_wrapper_run_does_not_register_ai_plugin():
    received: dict[str, object] = {}

    def fake_pytest_runner(args, **kwargs):
        received["args"] = args
        received["kwargs"] = kwargs
        return pytest.ExitCode.OK

    result = ai_runner.run_pytest(["tests/ui"], ai_enabled=False, pytest_runner=fake_pytest_runner)

    assert result == 0
    assert received == {"args": ["tests/ui"], "kwargs": {}}


def test_demo_failure_requires_explicit_ai_opt_in():
    with pytest.raises(SystemExit) as error:
        ai_runner.main(["--demo-failure"])

    assert error.value.code == 2


def test_demo_failure_routes_only_the_demo_through_ai_analysis(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run_pytest(args, ai_enabled):
        captured["args"] = args
        captured["ai_enabled"] = ai_enabled
        return int(pytest.ExitCode.TESTS_FAILED)

    monkeypatch.setattr(ai_runner, "run_pytest", fake_run_pytest)
    result = ai_runner.main(["--ai-analysis", "--demo-failure"])

    assert result == int(pytest.ExitCode.TESTS_FAILED)
    assert captured == {
        "args": ["--include-ai-failure-demo", str(ai_runner.DEMO_TEST_PATH)],
        "ai_enabled": True,
    }


def test_ai_analysis_is_not_invoked_when_no_tests_fail():
    class TrackingAnalyzer:
        called = False

        def analyze(self, _failures):
            self.called = True
            return ai_runner.AnalysisOutcome("completed", response=valid_response())

    analyzer = TrackingAnalyzer()
    plugin = ai_runner.FailureAnalysisPlugin(analyzer=analyzer)
    plugin.pytest_sessionfinish(SimpleNamespace(), int(pytest.ExitCode.OK))

    assert analyzer.called is False
    assert plugin.outcome.status == "skipped"
    assert "No failed tests" in plugin.outcome.reason


def test_wrapper_preserves_original_pytest_exit_code_when_analysis_fails():
    expected = int(pytest.ExitCode.TESTS_FAILED)

    class RaisingAnalyzer:
        def analyze(self, _failures):
            raise RuntimeError("simulated provider failure")

    def fake_pytest_runner(_args, plugins):
        plugin = plugins[0]
        plugin.failures.append(
            ai_runner.FailureEvidence(
                "test_demo.py::test_failure", "call", "AssertionError: mismatch"
            )
        )
        plugin.analyzer = RaisingAnalyzer()
        plugin.pytest_sessionfinish(SimpleNamespace(), expected)
        return pytest.ExitCode.TESTS_FAILED

    assert ai_runner.run_pytest([], ai_enabled=True, pytest_runner=fake_pytest_runner) == expected


def test_analysis_summary_escapes_generated_html_and_keeps_review_warning_visible():
    response = valid_response()
    response["recommended_fix"] = "<script>alert('unsafe')</script>"
    plugin = ai_runner.FailureAnalysisPlugin()
    plugin.outcome = ai_runner.AnalysisOutcome("completed", response=response)
    summary: list[str] = []

    plugin.pytest_html_results_summary([], summary, [])

    rendered = "".join(summary)
    assert "&lt;script&gt;" in rendered
    assert "<script>alert" not in rendered
    assert "human review required" in rendered.lower()
