import os

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


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
