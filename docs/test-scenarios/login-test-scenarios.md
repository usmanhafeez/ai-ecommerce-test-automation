# SauceDemo Login Test Scenarios

## Scope

This document covers authentication and validation on the SauceDemo login page at <https://www.saucedemo.com/>. It uses the public demo accounts:

| Account | Expected login behavior | Password |
|---|---|---|
| `standard_user` | Login succeeds | `secret_sauce` |
| `locked_out_user` | Login is rejected as locked out | `secret_sauce` |
| `problem_user` | Login is expected to succeed; known problems may occur in later application flows | `secret_sauce` |
| `performance_glitch_user` | Login is expected to succeed; response may be slower | `secret_sauce` |

The password is common public demo data and is included here only to make these scenarios executable by a tester. Do not reuse it for any real system.

## Scenario conventions

- Start each scenario from a fresh login page/session unless a scenario explicitly tests repeated attempts or session behavior.
- “Login page” means the SauceDemo sign-in form. “Inventory page” means the authenticated products page.
- For rejected credentials, the expected result is that the user remains unauthenticated and no inventory page is shown.
- Priorities reflect the impact and likelihood of a regression in this demo application's login feature.
- Exact copy of error text, element labels, and URL paths should be confirmed against the current application before turning these scenarios into automated assertions.

## Positive scenarios

| ID | Scenario and test data | Expected result | Priority |
|---|---|---|---|
| POS-01 | Sign in with `standard_user` / `secret_sauce`. | Authentication succeeds; user is taken to the inventory page and can see the product listing. | High |
| POS-02 | Sign in with `problem_user` / `secret_sauce`. | Authentication succeeds and the user reaches the inventory page. Any known product-page defects are recorded separately and do not count as login failure. | Medium |
| POS-03 | Sign in with `performance_glitch_user` / `secret_sauce`. | Authentication eventually succeeds and the user reaches the inventory page within the agreed response-time limit. | Medium |
| POS-04 | Submit valid credentials using the Login control (keyboard or pointer). | The form submits once and produces the same successful outcome regardless of supported submission method. | Medium |

## Negative scenarios

| ID | Scenario and test data | Expected result | Priority |
|---|---|---|---|
| NEG-01 | Sign in with `locked_out_user` / `secret_sauce`. | Login is rejected with a clear locked-account message; the user stays unauthenticated. | High |
| NEG-02 | Sign in with `standard_user` and an incorrect non-empty password. | Login is rejected with a generic invalid-credentials message; no authenticated content is accessible. | High |
| NEG-03 | Sign in with an unknown username and `secret_sauce`. | Login is rejected with a generic invalid-credentials message; no authenticated content is accessible. | High |
| NEG-04 | Sign in with both an unknown username and incorrect non-empty password. | Login is rejected without exposing whether the username exists. | High |
| NEG-05 | Submit a username with the wrong letter case (for example, `STANDARD_USER`) and the valid password. | Login is rejected if usernames are case-sensitive, as expected for the published account identifiers; no session is created. | Medium |
| NEG-06 | Submit a valid username with a password that differs by case (for example, `SECRET_SAUCE`). | Login is rejected; password matching is case-sensitive. | Medium |
| NEG-07 | Submit username with leading/trailing spaces and otherwise valid password. | Input is handled consistently with the application's documented policy; absent an explicit trim policy, credentials should not silently authenticate as a different value. | Medium |
| NEG-08 | Submit password with leading/trailing spaces and otherwise valid username. | Login is rejected unless whitespace normalization is an explicitly documented policy; no session is created. | Medium |

## Boundary and validation scenarios

| ID | Scenario and test data | Expected result | Priority |
|---|---|---|---|
| VAL-01 | Submit both fields empty. | Login is rejected; required-field validation is displayed and no session is created. | High |
| VAL-02 | Submit username only; leave password empty. | Login is rejected; password-required validation is displayed. | High |
| VAL-03 | Submit password only; leave username empty. | Login is rejected; username-required validation is displayed. | High |
| VAL-04 | Submit whitespace-only username and valid password. | Whitespace is not accepted as a valid account identifier; login is rejected with validation or generic credential feedback. | Medium |
| VAL-05 | Submit valid username and whitespace-only password. | Whitespace is not accepted as a valid password; login is rejected. | Medium |
| VAL-06 | Verify password input is masked while typing and after entry. | Password characters are obscured by default; they are not rendered as plain text in the field. | Medium |
| VAL-07 | Submit values at the accepted input length boundary, if a defined limit exists, then one character below/above it. | Values within the documented limit are handled; values beyond the limit are safely rejected or constrained without layout failure or unintended authentication. | Low |
| VAL-08 | Paste a long username/password value beyond normal credential lengths. | Page remains responsive; input and submission are handled safely, with no crash or unintended authentication. | Low |
| VAL-09 | Submit after correcting a previous validation error with valid credentials. | The stale error clears or is replaced; valid credentials authenticate successfully. | Medium |
| VAL-10 | Dismiss the displayed error using its close control, if present. | Error feedback is dismissed without changing authentication state; the form remains usable. | Low |

## Security-related scenarios

These checks are appropriate as bounded checks on the public demo. Do not perform high-volume guessing, denial-of-service, or intrusive security testing against the shared public service.

| ID | Scenario and test data | Expected result | Priority |
|---|---|---|---|
| SEC-01 | Inspect the password field and visible page while entering a password. | Password is masked by default and is not displayed in a separate visible element. | Medium |
| SEC-02 | Submit strings containing common markup/script payloads in username and password fields. | Inputs are treated as data; no script executes, no markup is injected, and authentication is rejected. | High |
| SEC-03 | Submit SQL-like special-character strings in both credential fields. | Inputs do not cause an application error or authentication bypass; login is rejected safely. | High |
| SEC-04 | Compare responses for an unknown username and a known username with a wrong password. | User-facing feedback does not reveal account existence beyond the intentionally published locked-account behavior. | Medium |
| SEC-05 | Verify the login page is served over HTTPS and credentials are submitted over HTTPS. | Browser uses HTTPS without a downgrade to HTTP; credentials are not sent in a cleartext URL or query string. | High |
| SEC-06 | Inspect the address bar after a failed login and after successful login. | Password and submitted credentials are not present in URL, query parameters, or fragment. | High |
| SEC-07 | Use browser back after successful authentication, then sign out if logout is available. | Protected content follows the application's session policy; after logout, protected content is not left accessible as an authenticated page. | Medium |
| SEC-08 | Attempt a small, manual sequence of invalid credentials, within normal demo use. | No credentials are accepted accidentally; errors remain safe and no sensitive implementation detail is exposed. Record whether throttling exists, but do not infer production-grade brute-force protection from this demo. | Low |

## Duplicate review

Scenarios were checked for overlapping intent. Empty-field checks (VAL-01–VAL-03) are separated by which required value is missing. Invalid username, invalid password, and invalid-both checks (NEG-02–NEG-04) distinguish credential combinations and include account-enumeration feedback in the combined case. Whitespace-only inputs (VAL-04–VAL-05) are distinct from padding a valid credential (NEG-07–NEG-08). Password masking (VAL-06 and SEC-01) appears in both sections because one is a UI validation check and the other states its security purpose; they are the same underlying check and should be implemented once with both tags if this document is converted into a test suite. No other exact duplicate scenario was identified.

## Assumptions and limitations

1. The supplied four account names are valid public demo accounts, and `secret_sauce` is their shared password, as listed by SauceDemo's public training materials and login-page guidance.
2. `standard_user` authenticates successfully; `locked_out_user` is rejected as locked out. `problem_user` and `performance_glitch_user` are treated as accounts expected to authenticate; their names refer to issues that may affect later behavior or response time.
3. Username and password matching are assumed case-sensitive. Confirm this against the current application before treating it as a requirement.
4. Whitespace is not assumed to be normalized. The expected behavior should be explicitly agreed if trimming is desired.
5. No maximum input lengths or detailed validation rules were supplied. VAL-07 is conditional on confirming a product limit; no arbitrary exact length is asserted.
6. A response-time threshold for `performance_glitch_user` was not supplied. Agree a limit and measurement method before making POS-03 a strict pass/fail check.
7. Current exact field labels, error copy, routing, and error-dismiss behavior were not verified live during document preparation. Confirm these before automation.
8. SauceDemo is a shared training application with publicly known credentials. Lockout, rate-limit, account-enumeration, and session-control checks here are observations of demo behavior, not assurance of production security controls.

## Additional scenarios recommended

- **Session persistence and logout:** Verify whether a successful session survives refresh or a new tab as intended, and verify logout invalidates access. This extends login into session lifecycle coverage.
- **Direct protected-page access:** Open the inventory route without logging in and verify the application redirects or otherwise denies access.
- **Accessibility and usability:** Check labels and accessible names, keyboard-only operation, focus order, visible focus, error announcement to assistive technology, and zoom/reflow.
- **Cross-browser and responsive behavior:** Confirm login on the supported browser/device matrix and at narrow viewport sizes.
- **Operational resilience:** Define acceptable latency for all accounts and assess behavior during a transient network failure, without sending load to the public demo.
- **Credential transport and session cookie review:** Where browser developer tools or an approved proxy are available, review secure transport and cookie flags. Treat findings as observations because the demo does not define production security requirements.

## Reference

- Sauce Labs training material depicting the SauceDemo login and published accounts: <https://saucelabs-training.github.io/slides.pdf>
- Application under test: <https://www.saucedemo.com/>
