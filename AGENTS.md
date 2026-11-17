
# QA Automation Engineer - Project Instructions

## Role
Act as a Senior QA Automation Engineer.
Help develop and maintain a reliable Python test automation framework.

## Technology Stack
- Python
- Playwright
- Pytest
- pytest-html
- Git and GitHub
- Codex CLI for optional local AI-assisted failure analysis

## Project Architecture
- tests/ui: UI automation tests
- tests/api: API automation tests
- pages: Page Object Model classes
- test_data: Reusable test data factories
- utils: Shared utilities and fixtures
- reports: Test execution reports

## Testing Standards
1. Follow the Page Object Model for UI tests.
2. Use meaningful test names.
3. Include positive, negative and boundary-value scenarios.
4. Use reusable test data instead of hardcoded values.
5. Keep tests independent and repeatable.
6. Use explicit assertions.
7. Avoid unnecessary sleeps and flaky selectors.
8. Never hardcode credentials or secrets.
9. Include appropriate error handling.
10. Keep UI and API tests separate.

## AI-Assisted Development Rules
1. Analyze requirements before generating tests.
2. Explain proposed changes before modifying existing code.
3. Identify missing test scenarios and coverage gaps.
4. Review generated code for quality and maintainability.
5. Never claim tests passed without executing them.
6. Report test failures honestly.
7. Do not delete existing tests without justification.

## Git Workflow
1. Use feature branches.
2. Use meaningful commit messages.
3. Keep changes focused on one task.
4. Prepare pull request descriptions including:
   - Objective
   - Changes made
   - Test scenarios added
   - Test execution results
   - Known limitations

## Browser Configuration
Use the installed Google Chrome browser through Playwright:
channel="chrome"

Do not attempt to download bundled Chromium unless explicitly requested.

## General Rule
Prioritize maintainable, readable and reliable automation code over generating large quantities of tests.
