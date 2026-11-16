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
| Git and GitHub | Version control and collaborative feature workflow. |
| GitHub Actions | Continuous integration for the full pytest suite. |
| Codex | AI-assisted analysis, scenario development, implementation support, and review. |

The pinned dependency set also includes Requests and Faker for potential shared tooling. API automation and Faker-based data generation are not currently implemented.

## Application Under Test

[SauceDemo](https://www.saucedemo.com/) is a public demo e-commerce application intended for software testing practice. The current UI suite covers its login flow and an inventory page smoke check. As a shared public demo, its availability and behavior may change independently of this repository.

## Project Structure

```text
.
├── .gitignore
├── AGENTS.md
├── README.md
├── docs/
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
│   └── ui/
│       ├── __init__.py
│       ├── test_browser.py
│       └── test_login.py
├── utils/
│   └── __init__.py
├── pytest.ini
└── requirements.txt
```

| Path | Purpose |
|---|---|
| `tests/ui/` | Browser smoke and login UI tests. |
| `tests/api/` | Reserved for API tests; no API test cases are implemented yet. |
| `pages/` | Page Object Model classes for login and inventory interactions and locators. |
| `test_data/` | Reusable SauceDemo URL and account test data. |
| `tests/conftest.py` | Function-scoped Playwright browser, isolated context, and page fixtures. |
| `docs/test-scenarios/` | Login scenario specification, including verified and pending coverage. |
| `pytest.ini` | Pytest discovery paths and output options. |
| `requirements.txt` | Pinned Python dependencies. |
| `AGENTS.md` | Project-specific QA, testing, browser, and Git guidance. |
| `.gitignore` | Excludes local environments, caches, reports, and `.env` files. |

## Automated Test Coverage

The current automated suite includes:

- Successful `standard_user` login, including the inventory URL, logo, and products list.
- Empty username and password validation.
- Username provided with a missing password.
- Password provided with a missing username.
- Rejection of the locked-out demo account, including remaining on the login page.
- A browser smoke test that launches Chrome and checks navigation to `example.com`.

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

## Continuous Integration

The [GitHub Actions workflow](.github/workflows/tests.yml) runs automatically on pushes to `main` and `feature/login-test-scenarios`, and on pull requests targeting `main`.

The workflow runs on `ubuntu-latest` with Python 3.14. It installs the project dependencies from `requirements.txt`, installs Playwright Chromium and its required system dependencies, then runs the full suite with `python -m pytest`.

Local development defaults to installed Google Chrome through Playwright's `channel="chrome"`. CI sets `PLAYWRIGHT_CHANNEL=chromium`, which uses Playwright-managed Chromium instead. This keeps the local Mac setup intact while allowing CI to use its installed browser dependencies.

## Test Results and Project Status

The initial GitHub Actions run completed successfully on `main` ([run details](https://github.com/usmanhafeez/ai-ecommerce-test-automation/actions/runs/43949743327)). The latest verified test result is **6 passed**: five login UI tests and one browser smoke test. This records the result of that run and does not guarantee future runs will pass. Browser or public demo availability, application changes, and environment differences can affect later results.

## Framework Design

- **Page Object Model:** `LoginPage` encapsulates login form locators and actions. `InventoryPage` exposes the inventory logo, products list, and add-to-cart button locators. Tests use these objects rather than redefining selectors.
- **Function-scoped fixtures:** `tests/conftest.py` creates a browser, isolated browser context, and page for each test, then closes them during fixture teardown. This keeps login state independent between tests.
- **Reusable test data:** SauceDemo's login URL and demo account values are centralized in `test_data/saucedemo.py` instead of repeated in test functions. The public demo password is test data, not a production credential.
- **Explicit assertions:** Tests assert exact validation messages and observable post-login URL and page content. Playwright's retrying assertions are used for page navigation and visibility checks; no fixed sleeps are used.
- **Test independence:** Each login test begins at the login URL and uses a fresh page context supplied by the function-scoped fixture.

## Git Workflow

Develop changes on a focused feature branch rather than directly on `main`. Use a clear commit message and open a pull request for review. A pull request should describe its objective, implementation, test scenarios, test execution results, and known limitations. Do not report a test as passing unless it was run and passed.

## Future Enhancements

- Add API automation under `tests/api/` using the existing Requests dependency.
- Add more e-commerce scenarios, such as inventory browsing, cart operations, and checkout, after defining their requirements and expected behavior.
- Expand CI reporting and artifact retention; no report generation pipeline is currently configured.
