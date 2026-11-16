from playwright.sync_api import Locator, Page


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_input: Locator = page.get_by_label("Username")
        self.password_input: Locator = page.get_by_label("Password")
        self.login_button: Locator = page.get_by_role(
            "button", name="Login", exact=True
        )
        self.error_message: Locator = page.get_by_role("alert")

    def enter_username(self, username: str) -> None:
        self.username_input.fill(username)

    def enter_password(self, password: str) -> None:
        self.password_input.fill(password)

    def click_login(self) -> None:
        self.login_button.click()

    def login(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        return self.error_message.inner_text()
