from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from test_data.saucedemo import (
    DEMO_PASSWORD,
    LOCKED_OUT_USERNAME,
    SAUCEDEMO_LOGIN_URL,
    STANDARD_USERNAME,
)


def test_standard_user_can_log_in_and_view_inventory(page: Page) -> None:
    page.goto(SAUCEDEMO_LOGIN_URL)
    login_page = LoginPage(page)
    inventory_page = InventoryPage(page)

    login_page.login(STANDARD_USERNAME, DEMO_PASSWORD)

    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(inventory_page.logo).to_be_visible()
    expect(inventory_page.logo).to_have_text("Swag Labs")
    expect(inventory_page.products_list).to_be_visible()


def test_login_with_both_fields_empty_shows_username_required_error(
    page: Page,
) -> None:
    page.goto(SAUCEDEMO_LOGIN_URL)
    login_page = LoginPage(page)

    login_page.click_login()

    assert login_page.get_error_message() == "Epic sadface: Username is required"


def test_login_with_username_and_empty_password_shows_password_required_error(
    page: Page,
) -> None:
    page.goto(SAUCEDEMO_LOGIN_URL)
    login_page = LoginPage(page)

    login_page.enter_username(STANDARD_USERNAME)
    login_page.click_login()

    assert login_page.get_error_message() == "Epic sadface: Password is required"


def test_login_with_password_and_empty_username_shows_username_required_error(
    page: Page,
) -> None:
    page.goto(SAUCEDEMO_LOGIN_URL)
    login_page = LoginPage(page)

    login_page.enter_password(DEMO_PASSWORD)
    login_page.click_login()

    assert login_page.get_error_message() == "Epic sadface: Username is required"


def test_locked_out_user_cannot_log_in(page: Page) -> None:
    page.goto(SAUCEDEMO_LOGIN_URL)
    login_page = LoginPage(page)

    login_page.login(LOCKED_OUT_USERNAME, DEMO_PASSWORD)

    assert (
        login_page.get_error_message()
        == "Epic sadface: Sorry, this user has been locked out."
    )
    expect(page).to_have_url(SAUCEDEMO_LOGIN_URL)
