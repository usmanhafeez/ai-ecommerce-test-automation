from playwright.sync_api import Page


def test_configured_browser_can_navigate(page: Page) -> None:
    page.goto("https://example.com")

    assert page.title() == "Example Domain"
