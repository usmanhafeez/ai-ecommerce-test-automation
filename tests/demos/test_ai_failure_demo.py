"""DEMONSTRATION ONLY: an intentionally injected failure for AI-assisted analysis.

This test is not evidence of a genuine SauceDemo application defect.
"""

from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.saucedemo import DEMO_PASSWORD, SAUCEDEMO_LOGIN_URL, STANDARD_USERNAME


def test_demo_expected_inventory_product_is_visible(page: Page) -> None:
    """Intentionally fail on an absent demo-only product to demonstrate AI analysis."""
    page.goto(SAUCEDEMO_LOGIN_URL)
    LoginPage(page).login(STANDARD_USERNAME, DEMO_PASSWORD)

    inventory_page = InventoryPage(page)
    expect(inventory_page.products_list).to_be_visible()

    demo_only_product = page.get_by_role(
        "heading", name="AI Analysis Demo Product", exact=True
    )
    expect(
        demo_only_product,
        message=(
            "Intentional demonstration failure: this demo-only product heading is not "
            "part of SauceDemo and is expected to remain absent."
        ),
    ).to_be_visible(timeout=3_000)
