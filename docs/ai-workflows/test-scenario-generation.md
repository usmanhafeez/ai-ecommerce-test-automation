# AI-Assisted Test Scenario Generation: SauceDemo Login

## Purpose

This example shows how an AI assistant can help turn existing project guidance, page objects, test data, and automated tests into a reviewable login scenario set. It is a design artifact only; scenarios marked as proposed are not automated test cases.

## Inputs reviewed

- `AGENTS.md` — project architecture, Page Object Model, repeatability, explicit assertions, reusable test data, and browser requirements.
- `README.md` — framework design, test coverage, browser setup, and current project status.
- `pages/login_page.py` and `pages/inventory_page.py` — current Playwright locators and available page actions.
- `test_data/saucedemo.py` — login URL and reusable account identifiers.
- `tests/ui/test_login.py` — the five existing login UI tests.
- `docs/test-scenarios/login-test-scenarios.md` — previously recorded verified behavior and unresolved questions.

## Evidence and scope

The current automated suite covers these observed outcomes:

- `standard_user` logs in and reaches `https://www.saucedemo.com/inventory.html`; the test asserts the inventory logo and products list.
- Empty username and password produce `Epic sadface: Username is required`.
- A supplied username with an empty password produces `Epic sadface: Password is required`.
- A supplied password with an empty username produces `Epic sadface: Username is required`.
- `locked_out_user` is rejected with `Epic sadface: Sorry, this user has been locked out.` and remains at the login URL.

The test data module defines `SAUCEDEMO_LOGIN_URL`, `STANDARD_USERNAME`, `LOCKED_OUT_USERNAME`, and `DEMO_PASSWORD`. The canonical scenario catalog refers to these reusable names rather than repeating a password literal.

No exact invalid-credential error text, username/password case policy, whitespace normalization rule, or maximum input length is established by the reviewed files. Scenarios depending on those details are explicitly marked for manual verification. Expected results in those cases describe the behavior to confirm, not a claim about current application behavior.

## Canonical scenario catalog

The canonical login scenarios, including their IDs, priorities, preconditions, steps, expected results, and coverage status, are maintained in [login-test-scenarios.md](../test-scenarios/login-test-scenarios.md). Use that document as the source of truth rather than duplicating the catalog here. This workflow describes how to review evidence, identify gaps, draft or refine scenarios, and submit proposed changes to human QA review.

## AI-assisted generation and human review

AI was used to organize the supplied project evidence into uniquely identified scenarios, map existing tests to that scenario set, and surface gaps. The draft was refined by excluding unverified error copy, normalization rules, and input limits, and by distinguishing an expected security requirement from observed application behavior.

Human QA review remains necessary to validate assumptions against the current public application, define product policies where they are missing, assess the safety and value of boundary/security checks, remove redundant scenarios, and approve any scenario before automation. AI-generated scenarios are proposals until that review is complete.

## Reusable prompt

Copy and adapt the following prompt to repeat the exercise:

> Act as a Senior QA Engineer specialising in AI-assisted test design. Review `AGENTS.md`, `README.md`, the relevant Page Objects, reusable test data, existing automated tests, and any current scenario documentation for **[application and feature]**.
>
> Produce a test scenario document at **[output path]**. First summarize existing behavior evidenced by the reviewed files and distinguish it from assumptions. Generate positive, negative, required-field, invalid-input, and applicable boundary scenarios. For every scenario provide a unique ID, title, priority (High/Medium/Low), preconditions, test steps, test data, expected result, and status (automated, manually verified, or requires manual verification).
>
> Do not invent application behavior, exact messages, validation rules, or input limits. Mark unknowns as requiring manual verification and state what evidence is needed. Map existing tests to scenarios and identify unautomated coverage. Check for duplicates and keep the proposed initial automation scope focused. Explain how AI contributed and why a human QA review is needed. Include this reusable prompt in the output document. Do not generate code or modify files other than the requested document.
