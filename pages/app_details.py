from common.base import BasePage
from pages_element.app_details_element import AppDetailsLoc


class AppDetailsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

    def click_app(self):
        self.click(AppDetailsLoc.APP_CODE_TEXT)

    def click_create_module(self):
        self.click(AppDetailsLoc.CREATE_MODULE_BTN)

    def click_backend_template(self):
        self.click(AppDetailsLoc.BACKEND_TEMPLATE_LOC)

    def enter_module_name(self, module_name: str):
        self.fill(AppDetailsLoc.MODULE_NAME_LOC, module_name)

    def click_confirm_button(self):
        self.click(AppDetailsLoc.CONFIRM_BTN)