# AI-Assisted E-commerce Test Automation Framework

## Project Overview

This repository is a Python-based UI test automation framework for the public SauceDemo e-commerce demo application. Browser interactions are implemented with Playwright, and test discovery, execution, and reporting to the terminal are handled by Pytest.

Codex supports the QA development workflow by helping analyze requirements, design test scenarios, implement maintainable test code, and review changes. The automated tests themselves are executed by Playwright and Pytest; AI assistance does not replace test execution or its results.

## Project Objectives

- Demonstrate practical QA automation engineering skills through focused, repeatable UI tests.
- Apply the Page Object Model to separate page interactions from test assertions.
- Use reusable, function-scoped browser fixtures and shared test data.
- Demonstrate a Git workflow based on feature branches, focused commits, and pull requests.
- Demonstrate AI-assisted scenario design, implementation, and code review while reporting test results accurately.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Test and framework implementation language. |
| Playwright | Browser automation through its synchronous Python API. |
| Pytest | Test discovery, fixtures, execution, and assertions. |
| pytest-html | Self-contained HTML reports for Pytest runs. |
| Git and GitHub | Version control and collaborative feature workflow. |
| GitHub Actions | Continuous integration for the full pytest suite. |
| Codex | AI-assisted analysis, scenario development, implementation support, and review. |

The pinned Python dependencies are Playwright, Pytest, and pytest-html, as listed in `requirements.txt`. Codex CLI is an optional local tool for failure analysis; it is not a Python dependency.

## Application Under Test

[SauceDemo](https://www.saucedemo.com/) is a public demo e-commerce application intended for software testing practice. The current UI suite covers its login flow and an inventory page smoke check. As a shared public demo, its availability and behavior may change independently of this repository.

## Project Structure

```text
.
├── .gitignore
├── AGENTS.md
├── README.md
├── docs/
│   ├── ai-workflows/
│   │   ├── failure-analysis.md
│   │   └── test-scenario-generation.md
│   └── test-scenarios/
│       └── login-test-scenarios.md
├── pages/
│   ├── __init__.py
│   ├── inventory_page.py
│   └── login_page.py
├── test_data/
│   ├── __init__.py
│   └── saucedemo.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── api/
│   │   └── __init__.py
│   ├── demos/
│   │   └── test_ai_failure_demo.py
│   ├── unit/
│   │   └── test_run_tests_with_ai.py
│   └── ui/
│       ├── __init__.py
│       ├── test_browser.py
│       └── test_login.py
├── scripts/
│   ├── failure_analysis.schema.json
│   └── run_tests_with_ai.py
├── utils/
│   └── __init__.py
├── pytest.ini
└── requirements.txt
```

| Path | Purpose |
|---|---|
| `tests/ui/` | Browser smoke and login UI tests. |
| `tests/demos/` | Intentional, opt-in demonstrations; excluded from normal test collection. |
| `tests/unit/` | Unit tests for the optional Codex failure-analysis wrapper. |
| `tests/api/` | Reserved for API tests; no API test cases are implemented yet. |
| `scripts/` | Optional test runner and response schema for local Codex failure analysis. |
| `pages/` | Page Object Model classes for login and inventory interactions and locators. |
| `test_data/` | Reusable SauceDemo URL and account test data. |
| `tests/conftest.py` | Function-scoped Playwright browser, isolated context, and page fixtures. |
| `docs/test-scenarios/` | Login scenario specification, including verified and pending coverage. |
| `pytest.ini` | Pytest discovery paths and output options. |
| `requirements.txt` | Pinned Python dependencies. |
| `AGENTS.md` | Project-specific QA, testing, browser, and Git guidance. |
| `.gitignore` | Excludes local environments, caches, reports, `.DS_Store`, and environment files while allowing `.env.example`. |

## Automated Test Coverage

The current automated suite includes:

- Successful `standard_user` login, including the inventory URL, logo, and products list.
- Empty username and password validation.
- Username provided with a missing password.
- Password provided with a missing username.
- Rejection of the locked-out demo account, including remaining on the login page.
- A browser smoke test that launches Chrome and checks navigation to `example.com`.
- Unit tests for the optional Codex wrapper, including sanitization, schema validation, failure handling, and exit-code preservation.

The login page and inventory locators were inspected against the live SauceDemo DOM. Add-to-cart controls are represented by an InventoryPage locator, but an add-to-cart interaction is not currently tested.

Detailed scenarios and verification status are documented in [`docs/test-scenarios/login-test-scenarios.md`](docs/test-scenarios/login-test-scenarios.md).

## Setup Instructions

### Prerequisites

- Python 3 with virtual environment support.
- Git.
- Google Chrome installed locally. Playwright launches this installed browser using `channel="chrome"`.

Clone the repository and enter its directory:

```bash
git clone https://github.com/usmanhafeez/ai-ecommerce-test-automation.git
cd ai-ecommerce-test-automation
```

Create and activate a virtual environment, then install the pinned requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The project uses installed Google Chrome through Playwright's `channel="chrome"` setting. It does not require downloading Playwright's bundled Chromium browser.

## Running Tests

With the virtual environment activated, run all tests:

```bash
python -m pytest
```

Run only the login UI tests:

```bash
python -m pytest tests/ui/test_login.py
```

Alternatively, without activating the environment on macOS/Linux:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/ui/test_login.py
```

## Test Reports and Failure Evidence

Pytest generates a self-contained HTML report at `reports/pytest-report.html` for each run, including runs with failed tests. Open that file in a browser to review the test outcomes, failure messages, and tracebacks. For example, on macOS:

```bash
open reports/pytest-report.html
```

When a UI test fails during its test call, the framework attempts to save a full-page screenshot under `reports/screenshots/` using a readable test-based filename with a timestamp and unique suffix. The screenshot is attached to that test's HTML report entry when capture succeeds. Failure details and an **AI analysis readiness** note are also included. The note explains that AI analysis is optional and can be invoked through the wrapper; normal Pytest runs do not invoke Codex. Evidence collection errors are reported as warnings and do not replace the original test result.

### Optional Codex Failure Analysis

The ordinary Pytest command does not invoke AI. To opt in, run the wrapper instead:

```bash
python scripts/run_tests_with_ai.py --ai-analysis
```

The wrapper runs the suite once and calls the installed, authenticated Codex CLI only if tests fail. It submits minimal sanitized failure text only; screenshots, source files, credentials, and the demo password are not sent. Analysis is time-limited, schema-validated, and added to the HTML report with a human-review warning. If sanitization is uncertain or Codex is unavailable, the report records the reason and the original Pytest exit status is preserved.

To run the deliberately failing demonstration by itself, opt in to both the demo and Codex analysis:

```bash
python scripts/run_tests_with_ai.py --ai-analysis --demo-failure
```

This test signs in to SauceDemo, verifies the real products list, then expects a clearly labelled demo-only product heading that is intentionally absent. Its failing result is expected and is not an application defect. The wrapper returns Pytest's failure exit code. The demo is excluded from both `python -m pytest` and `python -m pytest tests`. Before running the normal suite, archive the demonstration report if you want to keep it separately:

```bash
cp reports/pytest-report.html reports/ai-failure-demo-report.html
```

Codex CLI is an optional local prerequisite, not a Python dependency. Its hosted provider may have usage limits or costs. The GitHub Actions workflow continues to run `python -m pytest` and does not invoke the wrapper or Codex.

## Continuous Integration

The [GitHub Actions workflow](.github/workflows/tests.yml) runs automatically on pushes to `main` and `feature/login-test-scenarios`, and on pull requests targeting `main`.

The workflow runs on `ubuntu-latest` with Python 3.14. It installs the project dependencies from `requirements.txt`, installs Playwright Chromium and its required system dependencies, then runs the full suite with `python -m pytest`.

Local development defaults to installed Google Chrome through Playwright's `channel="chrome"`. CI sets `PLAYWRIGHT_CHANNEL=chromium`, which uses Playwright-managed Chromium instead. This keeps the local Mac setup intact while allowing CI to use its installed browser dependencies.

## Test Results and Project Status

The initial GitHub Actions run completed successfully on `main` ([run details](https://github.com/usmanhafeez/ai-ecommerce-test-automation/actions/runs/43949743327)). The latest locally verified result is **36 passed**: five login UI tests, one browser smoke test, and 30 unit tests for the optional Codex wrapper. This records that local run and does not guarantee future runs will pass. Browser or public demo availability, application changes, and environment differences can affect later results.

## Framework Design

- **Page Object Model:** `LoginPage` encapsulates login form locators and actions. `InventoryPage` exposes the inventory logo, products list, and add-to-cart button locators. Tests use these objects rather than redefining selectors.
- **Function-scoped fixtures:** `tests/conftest.py` creates a browser, isolated browser context, and page for each test, then closes them during fixture teardown. This keeps login state independent between tests.
- **Reusable test data:** SauceDemo's login URL and demo account values are centralized in `test_data/saucedemo.py` instead of repeated in test functions. The public demo password is test data, not a production credential.
- **Explicit assertions:** Tests assert exact validation messages and observable post-login URL and page content. Playwright's retrying assertions are used for page navigation and visibility checks; no fixed sleeps are used.
- **Test independence:** Each login test begins at the login URL and uses a fresh page context supplied by the function-scoped fixture.

## AI-Assisted QA Workflows

Codex assists QA engineers with test design and failure analysis. Pytest executes the tests, and Playwright drives the browser interactions; AI assistance does not replace test execution or establish application behavior on its own.

- **Test scenario generation:** Codex can help organize requirements and existing test evidence into reviewable scenarios, identify current coverage and gaps, and flag behavior that needs manual verification. See the [AI-assisted test scenario generation workflow](docs/ai-workflows/test-scenario-generation.md).
- **Test failure analysis:** Codex can help structure supplied test output, source excerpts, and browser evidence into an evidence-based analysis that distinguishes confirmed facts from hypotheses. See the [AI-assisted test failure analysis workflow](docs/ai-workflows/failure-analysis.md).

AI-generated recommendations require human QA review before they are accepted as correct or used to guide code changes. Codex must not modify code automatically as part of failure analysis; changes require explicit human approval.

## Git Workflow

Develop changes on a focused feature branch rather than directly on `main`. Use a clear commit message and open a pull request for review. A pull request should describe its objective, implementation, test scenarios, test execution results, and known limitations. Do not report a test as passing unless it was run and passed.

## Future Enhancements

- Add API automation under `tests/api/`, selecting and pinning an HTTP client dependency if the implementation requires one.
- Add more e-commerce scenarios, such as inventory browsing, cart operations, and checkout, after defining their requirements and expected behavior.
- Retain CI reports as workflow artifacts. Pytest-html generates `reports/pytest-report.html`, but GitHub Actions does not currently upload or retain it as an artifact.
