# AI-Assisted Pytest Failure Analysis Workflow

## Purpose

This workflow helps a QA engineer use Codex to investigate a failed Python, Playwright, or Pytest test in this project. Codex organizes the supplied evidence, compares actual results with the test's intended behavior, and proposes likely causes and next steps. It does not determine application correctness from an error message alone, and its proposed causes remain hypotheses until verified.

Human review owns the diagnosis and any code change. **Codex must not modify application code, tests, Page Objects, fixtures, dependencies, or configuration automatically. It must wait for explicit human approval before making any change.**

## Project-specific context

- UI tests are under `tests/ui/`; the current suite uses Playwright's synchronous Python API and Pytest.
- `LoginPage` centralizes login locators and actions. `InventoryPage` centralizes inventory locators.
- `tests/conftest.py` provides function-scoped browser, context, and page fixtures. Each test receives an isolated browser context and page, with cleanup during fixture teardown.
- The browser fixture defaults to installed Google Chrome using `channel="chrome"`. CI sets `PLAYWRIGHT_CHANNEL=chromium` to use Playwright-managed Chromium. Include this environment distinction when investigating browser-specific failures.
- Reusable SauceDemo values are in `test_data/saucedemo.py`. Do not paste real credentials, tokens, cookies, or other secrets into an AI prompt. Refer to constants or redact values.
- Tests use retrying Playwright assertions for important navigation and visibility checks. Avoid recommending fixed sleeps as a first response to timing failures.
- The public SauceDemo application and external network can change or become unavailable. Do not attribute a failure to the application without evidence.

## What to provide to Codex

Provide enough evidence to reproduce and reason about the failure:

1. **Test output:** the exact command run, Pytest summary, failed test name, complete relevant assertion message, and stack trace. Preserve the first failure before rerunning.
2. **Relevant source code:** the failing test, referenced Page Object methods/locators, `tests/conftest.py`, relevant `test_data` entries (redacted or named by constant), and any relevant `pytest.ini` or workflow settings.
3. **Execution environment:** local or GitHub Actions, Python/Pytest/Playwright versions when available, operating system, browser, `PLAYWRIGHT_CHANNEL` value, and whether the failure is repeatable.
4. **Browser evidence:** attach a screenshot or Playwright trace if one was captured and is available. Include the URL, visible page state, and relevant console/network error details when available. Do not assume screenshots or traces exist if the run did not produce them.
5. **Recent context:** recent changes that may affect this test, test data, selectors, application behavior, or environment. Do not include unrelated source files.

Rerun only when it is useful to distinguish a reproducible failure from an intermittent one. Record each run separately and do not replace the original failure with a later passing result.

## Reusable Codex prompt

Copy this prompt and fill in the bracketed sections:

```text
Act as a Senior QA Automation Engineer investigating a failed test in this
Python, Playwright, and Pytest project. Analyze the failure; do not edit files,
run commands, install packages, or change code. Do not make changes unless I
later give explicit approval.

Project context:
- UI tests: tests/ui/
- Page Objects: pages/
- Fixtures: tests/conftest.py
- Reusable test data: test_data/
- Playwright uses the synchronous Python API.
- Local browser defaults to installed Chrome (channel="chrome"); CI selects
  Playwright-managed Chromium with PLAYWRIGHT_CHANNEL=chromium.

Test command:
[paste exact command]

Environment:
[local or CI, OS, Python/Pytest/Playwright versions, browser, channel/env vars]

Failure output and stack trace:
[paste complete relevant Pytest output]

Relevant test, Page Object, fixture, test data, and configuration excerpts:
[paste only relevant excerpts; redact credentials, tokens, cookies, and secrets]

Screenshot or trace evidence, if available:
[attach it or describe the relevant visible state, URL, console/network errors]

Repeatability and recent relevant changes:
[state whether it failed once or repeatedly and list relevant changes]

Return the analysis using this exact structure:
1. Failed test and intended/expected behaviour
2. Actual behaviour observed in the supplied evidence
3. Primary failure category (choose one): application bug, test bug,
   locator issue, environment issue, test data issue, or flaky test
   - Add a secondary category only if evidence supports one.
4. Evidence
   - Confirmed facts (quote or point to the supplied output/source/evidence)
   - Hypotheses (clearly labelled; do not state them as facts)
5. Likely root cause, with alternatives if the evidence is inconclusive
6. Recommended fix (describe the smallest appropriate change; do not apply it)
7. Regression tests to consider
8. Confidence level: High, Medium, or Low, with a short reason
9. Missing evidence or a safe next diagnostic step, if needed

Do not invent application behaviour, error messages, DOM attributes, or test
results. Distinguish an assertion failure from a setup error. Do not claim a
test passed unless supplied output shows that it passed. Do not recommend fixed
sleeps without first explaining why a state-based wait or retrying assertion is
not suitable. Ask for explicit human approval before changing any file.
```

## Required analysis format

Every analysis must include the following information, even when the answer is “unknown”:

| Field | What the analysis should report |
|---|---|
| Failed test and expected behaviour | Test function/file and the behavior its assertion is intended to protect, based on source or scenario documentation. |
| Actual behaviour | What the supplied run actually observed: error, URL, page state, timeout, or setup result. Do not infer beyond the evidence. |
| Failure category | Select a primary category from the six listed in the prompt. A secondary category is optional and must also be evidence-based. |
| Evidence | Separate confirmed facts from hypotheses. Reference the exact output, source excerpt, screenshot, trace, or environment detail. |
| Likely root cause | State the best-supported explanation, alternatives, and what evidence would distinguish them. |
| Recommended fix | Propose a focused change or diagnostic action without applying it. Keep Page Object, fixture, and test responsibilities in mind. |
| Regression tests to consider | Identify existing cases that should remain protected and any focused additional case worth considering. Do not claim it has been added or run. |
| Confidence level | High, Medium, or Low, with a concise rationale tied to evidence quality and completeness. |

### Failure category guidance

- **Application bug:** evidence points to the application violating a confirmed requirement or previously verified behavior.
- **Test bug:** test setup, sequencing, assertion, or test logic does not correctly represent the intended behavior.
- **Locator issue:** a selector does not resolve to the intended live element, is ambiguous, or is coupled to unstable DOM details. Check the actual page/DOM before concluding this.
- **Environment issue:** browser launch, operating system, dependency, network, CI configuration, or external service availability prevents the test from exercising the intended behavior.
- **Test data issue:** supplied values are missing, malformed, stale, or not appropriate for the scenario. Avoid exposing sensitive values.
- **Flaky test:** the same test has inconsistent outcomes under materially equivalent conditions. A single timeout is not sufficient evidence by itself; first gather repeatability data and inspect state-based waits and external dependencies.

## Confirmed facts versus hypotheses

Use explicit labels in the analysis:

- **Confirmed fact:** directly shown by the failure output, source code, browser artifact, or verified environment information supplied for this investigation.
- **Hypothesis:** a plausible explanation that is not yet established by that evidence.
- **Unknown:** required evidence or intended behavior has not been supplied.

For example, a stack trace showing a timeout waiting for a locator is a confirmed fact. “The application removed the element” is only a hypothesis unless a DOM snapshot or screenshot supports it. A mismatch between local Chrome and CI Chromium is a confirmed environment difference if reported, but it is not automatically the root cause.

## Human approval and changes

The output is analysis and recommendations only. Codex must not edit files, apply patches, delete tests, install dependencies, or alter browser/configuration settings during failure analysis. If a human wants a fix implemented, they must give a separate, explicit instruction after reviewing the diagnosis. Any later change should be focused, follow `AGENTS.md`, and be verified with tests only when requested or authorized.

## Optional local Pytest integration

The project includes an opt-in wrapper for local runs. The regular `python -m pytest` command and GitHub Actions workflow do not invoke Codex. Run:

```bash
python scripts/run_tests_with_ai.py --ai-analysis
```

The wrapper completes the Pytest run first and invokes Codex only when the option is enabled and failures were recorded. It submits only minimal failure identifiers and sanitized exception messages. It does not send screenshots, source files, test-data files, credentials, cookies, tokens, or the demo password. If sanitization is uncertain, the analysis is skipped with a reason. Codex runs with `--sandbox read-only`, an ephemeral session, a timeout, and the checked-in JSON schema. The result is escaped before it is inserted into the pytest-html summary. The original Pytest exit code is preserved when Codex is missing, unavailable, times out, or returns invalid output.

The report labels Codex content as AI-generated and requires human review. A valid JSON response is not evidence that its diagnosis is correct. Codex CLI must be installed and authenticated, and hosted-provider usage limits or costs may apply. No local model or direct API integration is used.

### Intentional failure demonstration

The demo test under `tests/demos/` is excluded from ordinary collection, including an explicit `python -m pytest tests` run. To run only the demo and opt in to Codex analysis:

```bash
python scripts/run_tests_with_ai.py --ai-analysis --demo-failure
```

The demo logs in with reusable test data, confirms the actual inventory list is visible, then intentionally expects a demo-only product heading that is absent. The failure is expected and does not indicate a SauceDemo defect. The command is expected to exit with Pytest's failing status. It writes `reports/pytest-report.html`; archive it as `reports/ai-failure-demo-report.html` before the next test run if you want to retain the demonstration report.

## Hypothetical example (not a real failure)

The following example is invented solely to demonstrate the format. It does not report an actual project test failure or a current SauceDemo behavior change.

**Supplied hypothetical failure:** `test_standard_user_can_log_in_and_view_inventory` times out waiting for the products-list locator. A hypothetical screenshot shows the inventory URL and the `Swag Labs` logo. A hypothetical DOM snapshot shows a visible product container but no `data-test="inventory-list"` attribute.

1. **Failed test and expected behaviour:** The successful-login test expects the inventory products list to become visible after standard-user login.
2. **Actual behaviour:** In this hypothetical evidence, the test times out resolving the products-list locator, while the screenshot shows the inventory page and logo.
3. **Primary category:** Locator issue.
4. **Evidence:**
   - **Confirmed facts in this hypothetical:** the locator timed out; the URL and logo are visible in the supplied screenshot; the DOM snapshot lacks the selector attribute used by the locator.
   - **Hypothesis:** the application markup changed and the selector no longer identifies the product container.
5. **Likely root cause:** The products-list selector no longer matches the live DOM. Confidence would be higher after confirming the screenshot and DOM came from the same failed run and checking whether the expected container is uniquely identifiable.
6. **Recommended fix:** Reinspect the live DOM and accessibility tree, then propose a stable locator consistent with the project’s locator standards. Do not change the Page Object until a human approves the evidence-based selector.
7. **Regression tests to consider:** Keep the successful-login assertions for the inventory URL and logo; retain a products-list visibility assertion using the approved locator.
8. **Confidence level:** Medium — the hypothetical DOM snapshot supports a selector mismatch, but a screenshot alone may not show the full DOM or explain why the attribute is absent.
9. **Missing evidence / next diagnostic step:** Confirm the DOM snapshot belongs to the failing run and inspect the element structure around the products container.
