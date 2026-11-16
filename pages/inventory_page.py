from playwright.sync_api import Locator, Page


class InventoryPage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.logo: Locator = page.get_by_text("Swag Labs", exact=True)
        self.products_list: Locator = page.locator(
            '[data-test="inventory-list"]'
        )
        self.add_to_cart_buttons: Locator = page.get_by_role(
            "button", name="Add to cart", exact=True
        )
