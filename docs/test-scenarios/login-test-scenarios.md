# SauceDemo Login Test Scenarios

## Scope and conventions

Application: <https://www.saucedemo.com/>. This document defines login-focused manual scenarios for the public demo. Automation is expected to use Python, pytest, Playwright, and installed Google Chrome (`channel="chrome"`) per [AGENTS.md](../../AGENTS.md).

Each case states its own preconditions, steps, and observable expected result. Use a fresh browser context or otherwise ensure an unauthenticated login page before each case. Do not infer behavior that is not listed as verified below. The priorities describe the recommended order for core login automation.

The public demo password is `secret_sauce`. It is public demo data, not a real credential. When scenarios are automated, follow project guidance and keep credentials out of test code by using configuration or shared test data.

## Manually verified behavior

The following outcomes were supplied as manually verified and are treated as facts for this document:

| Input | Exact observed result |
|---|---|
| Empty username and empty password | `Epic sadface: Username is required` |
| Username provided and password empty | `Epic sadface: Password is required` |
| `locked_out_user` / `secret_sauce` | `Epic sadface: Sorry, this user has been locked out.` |
| `standard_user` / `secret_sauce` | Login succeeds at `https://www.saucedemo.com/inventory.html`; the `Swag Labs` logo, products list, and Add to cart buttons are visible. |

## Automated behavior

The current login UI suite passed for the cases below. Automation checks the exact errors for validation and locked-account cases. For successful login, it checks the exact inventory URL, logo visibility and text, and products-list visibility. The password-only username-required result is covered by automation; it is not listed as manually verified.

## Core automation scope

| ID / Priority | Preconditions | Test steps | Expected result | Status |
|---|---|---|---|---|
| LOGIN-01 — High | Unauthenticated session; login page is loaded. | Leave both fields empty. Submit the form. | Login is rejected and the error reads exactly `Epic sadface: Username is required`. | **Automated; manually verified** |
| LOGIN-02 — High | Unauthenticated session; login page is loaded. | Enter a non-empty username (use `standard_user`). Leave password empty. Submit the form. | Login is rejected and the error reads exactly `Epic sadface: Password is required`. | **Automated; manually verified** |
| LOGIN-03 — High | Unauthenticated session; login page is loaded. | Enter `locked_out_user` and `secret_sauce`. Submit the form. | Login is rejected and the error reads exactly `Epic sadface: Sorry, this user has been locked out.` The user remains at the login URL. | **Automated; message manually verified** |
| LOGIN-04 — High | Unauthenticated session; login page is loaded. `standard_user` / `secret_sauce` is a manually verified working account. | Enter the credentials and submit the form. | URL is `https://www.saucedemo.com/inventory.html`; the `Swag Labs` logo and products list are visible. | **Automated and manually verified** |
| LOGIN-05 — Medium | Unauthenticated session; login page is loaded. `standard_user` is assumed to exist. | Enter `standard_user` and a non-empty incorrect password. Submit the form. | Login is rejected; no authenticated inventory page is displayed. Exact error copy is not specified until verified. | **Requires manual verification** |
| LOGIN-06 — Medium | Unauthenticated session; login page is loaded. The chosen username is assumed not to be a valid demo account. | Enter a clearly unknown username and `secret_sauce`. Submit the form. | Login is rejected; no authenticated inventory page is displayed. Exact error copy is not specified until verified. | **Requires manual verification** |
| LOGIN-07 — Medium | Unauthenticated session; login page is loaded. The account/password pair is assumed valid. | Enter `problem_user` and `secret_sauce`. Submit the form. | Authentication succeeds and the authenticated inventory/products page is displayed. Any downstream product behavior is outside this login assertion. | **Requires manual verification** |
| LOGIN-08 — Medium | Unauthenticated session; login page is loaded. The account/password pair is assumed valid. No response-time threshold has been defined. | Enter `performance_glitch_user` and `secret_sauce`. Submit the form. | Authentication succeeds and the authenticated inventory/products page is displayed. Do not assert a duration until a threshold and timing method are agreed. | **Requires manual verification** |
| DEFER-01 — High | Unauthenticated session; login page is loaded. | Leave username empty; enter `secret_sauce`; submit the form. | Login is rejected and the error reads exactly `Epic sadface: Username is required`. | **Automated; behavior verified by current test run** |

### Initial automation order

LOGIN-01 through LOGIN-04 and DEFER-01 are implemented and passing in the current suite. LOGIN-05 through LOGIN-08 remain future candidates after their account outcomes and error/page assertions have been verified. Keep the `performance_glitch_user` case functional; performance measurement is out of scope until an explicit threshold is set.

## Deferred scenarios requiring requirements or manual verification

These are not part of the initial automation scope. Each needs an agreed expectation or observable criterion before becoming an automated pass/fail test.

| ID | Preconditions | Test steps | Expected result to establish | Why deferred |
|---|---|---|---|---|
| DEFER-02: Case handling | Fresh unauthenticated login page; valid account data. | Try username with altered case, then password with altered case, in separate runs. | Confirm whether each field is case-sensitive; specify expected outcomes. | Current policy is unknown. |
| DEFER-03: Whitespace handling | Fresh unauthenticated login page; valid account data. | Test leading/trailing spaces and whitespace-only values separately in username and password. | Confirm whether whitespace is trimmed or significant; specify expected outcomes. | Current policy is unknown. |
| DEFER-04: Input length boundaries | Fresh unauthenticated login page; a documented length limit is available. | Submit values just below, at, and above the documented limit. | Values are accepted/rejected according to the documented limit, without unintended authentication. | No field length limit is known. |
| DEFER-05: Correcting an error | Fresh unauthenticated login page. | Submit an invalid or incomplete form; correct it with valid credentials; submit again. | Confirm whether old error feedback clears and successful login occurs. | Error-clearing and success behavior need observation. |
| DEFER-06: Error dismissal | Fresh unauthenticated login page; submit an input that produces an error. | Inspect for a dismissal control; if present, activate it. | Confirm control presence and that dismissing feedback leaves the form usable and unauthenticated. | Control existence and effect are unknown. |
| DEFER-07: Keyboard submission | Fresh unauthenticated login page; valid account data. | Fill both fields and submit using the keyboard. | Confirm keyboard submission is supported and results in the same authenticated state as pointer submission. | Key behavior and accessible form semantics need verification. |
| DEFER-08: Credential URL exposure / HTTPS | Login page loaded. | Observe initial URL and navigation/request URLs during both failed and successful submission. | Confirm HTTPS behavior and that credentials do not appear in URL, query, or fragment. | Requires browser/network inspection; no current observation supplied. |
| DEFER-09: Injection-oriented inputs | Fresh unauthenticated login page. | Submit a small, reviewed set of special-character or markup-like values. | Define specific observable checks for no script execution, unexpected markup, or authentication. | UI checks cannot establish broad injection security; scope and assertions need security review. |
| DEFER-10: Session and protected routes | Session/login behavior requirements defined. | Attempt direct inventory access unauthenticated; separately test refresh/back/logout behavior after login. | Specify redirect/denial and session invalidation behavior. | These are session-management scenarios, and expected policy is unknown. |
| DEFER-11: Performance | Agree threshold, environment, and timing boundaries. | Log in with `performance_glitch_user` and measure the defined interval. | Login completes within the approved threshold under the agreed conditions. | No threshold or measurement method exists. |

## Duplicate and scope review

- The previous password-masking cases in validation and security sections were duplicates; neither is retained in the core login suite. Add a single UI/security check later if required.
- The previous unknown-user plus wrong-password case duplicated the separate invalid-password and unknown-user cases for ordinary functional coverage. It is omitted. If account-enumeration checking is required, compare the user-facing outcomes of LOGIN-05 and LOGIN-06 as one separately scoped security assessment.
- The prior URL credential check and HTTPS check overlapped; they are consolidated into DEFER-08.
- The prior markup and SQL-like input cases were broad and did not prove security properties. They are replaced with one explicitly limited, deferred injection-input assessment (DEFER-09).
- The previous mixed back/logout case combined separate session behaviors; these are grouped as future session-management work in DEFER-10 and require distinct cases when specified.
- Pointer and keyboard submission are not asserted as one combined behavior. Keyboard submission is a separate deferred case; the pointer path is used in the core cases.
- No arbitrary maximum-length or long-input boundary is claimed. DEFER-04 requires an actual product limit.

## Locator guidance for later Playwright work

The live DOM inspection confirmed label-based username/password locators, a role/name Login button, and an alert error locator. The inventory logo is the exact text `Swag Labs`; the products list uses `[data-test="inventory-list"]`. The Add to cart role/name locator matched six buttons. For successful login, the automated test asserts the verified inventory URL, visible logo, and visible products list. Avoid generated CSS classes and positional selectors.

## Remaining assumptions

1. `problem_user` and `performance_glitch_user` with `secret_sauce` are assumed to authenticate; they are not covered by the current automated tests.
2. Invalid and unknown credential data for LOGIN-05/06 will be selected and checked before automation.
3. Case sensitivity, whitespace normalization, input limits, keyboard submission, error dismissal, HTTPS/session behavior, and performance expectations remain unknown as listed in deferred cases.
4. The browser automation target is installed Google Chrome through Playwright `channel="chrome"`, per project instructions.
