import base64
import os
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_html
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
AI_FAILURE_DEMO_ENABLED = False


def pytest_configure(config: pytest.Config) -> None:
    global AI_FAILURE_DEMO_ENABLED
    AI_FAILURE_DEMO_ENABLED = config.getoption("--include-ai-failure-demo", default=False)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    demos_dir = Path(__file__).resolve().parent / "demos"
    candidate = collection_path.resolve()
    if candidate == demos_dir or candidate.is_relative_to(demos_dir):
        return not config.getoption("--include-ai-failure-demo", default=False)
    return None


def pytest_html_results_summary(prefix: list[str], summary: list[str], postfix: list[str]) -> None:
    if AI_FAILURE_DEMO_ENABLED:
        summary.append(
            "<p><strong>DEMONSTRATION ONLY:</strong> This intentionally injected test failure "
            "demonstrates AI-assisted failure analysis. It is not a genuine SauceDemo "
            "application defect.</p>"
        )
    summary.append(
        "<p><strong>AI analysis readiness:</strong> Failure details and UI screenshots "
        "remain available in this report. AI analysis is optional: run "
        "<code>python scripts/run_tests_with_ai.py --ai-analysis</code> to invoke the Codex "
        "wrapper; normal Pytest runs do not invoke Codex. Screenshots are not sent to Codex.</p>"
    )


def pytest_html_results_table_header(cells: list[str]) -> None:
    cells.insert(1, '<th class="sortable" data-column-type="suite">Suite</th>')


def pytest_html_results_table_row(report: pytest.TestReport, cells: list[str]) -> None:
    suite = _test_suite_label(report.nodeid)
    cells.insert(1, f'<td class="col-suite">{suite}</td>')


def _test_suite_label(nodeid: str) -> str:
    if nodeid.startswith("tests/ui/"):
        return "UI"
    if nodeid.startswith("tests/unit/"):
        return "Unit"
    if nodeid.startswith("tests/demos/"):
        return "Demo"
    if nodeid.startswith("tests/api/"):
        return "API"
    return "Other"


@pytest.fixture
def browser() -> Browser:
    with sync_playwright() as playwright:
        channel = os.getenv("PLAYWRIGHT_CHANNEL", "chrome")
        if channel == "chromium":
            browser = playwright.chromium.launch(headless=True)
        else:
            browser = playwright.chromium.launch(channel=channel, headless=True)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    context = browser.new_context()
    try:
        yield context
    finally:
        context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    page = context.new_page()
    try:
        yield page
    finally:
        page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    extras = getattr(report, "extras", [])
    report.extras = extras
    try:
        failure_details = f"Test: {item.nodeid}\n\nTraceback and error:\n{report.longreprtext}"
        extras.append(pytest_html.extras.text(failure_details, name="Failure details"))
    except Exception as evidence_error:
        _warn_evidence_error(item, "adding failure details to the HTML report", evidence_error)

    tests_dir = Path(__file__).resolve().parent
    ui_test_dir = tests_dir / "ui"
    demo_test = tests_dir / "demos" / "test_ai_failure_demo.py"
    if not item.path.is_relative_to(ui_test_dir) and item.path != demo_test:
        return

    page = getattr(item, "funcargs", {}).get("page")
    if page is None:
        return

    try:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        readable_name = re.sub(r"[^A-Za-z0-9_-]+", "-", item.name).strip("-")[:100]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        screenshot_path = SCREENSHOTS_DIR / f"{readable_name}-{timestamp}-{uuid4().hex[:8]}.png"
        screenshot_bytes = page.screenshot(path=str(screenshot_path), full_page=True)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("ascii")
        extras.append(pytest_html.extras.png(screenshot_base64, name="Failure screenshot"))
    except Exception as evidence_error:
        _warn_evidence_error(item, "capturing or attaching the failure screenshot", evidence_error)


def _warn_evidence_error(item: pytest.Item, action: str, error: Exception) -> None:
    try:
        warnings.warn(
            f"Could not complete {action} for {item.nodeid}: {error}",
            RuntimeWarning,
            stacklevel=2,
        )
    except Exception:
        # Evidence reporting must never replace or change the original test result.
        pass
