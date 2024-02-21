from common.base import BasePage
from pages_element.app_list_element import AppListLoc


class AppListPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

    def click_create_app_button(self):
        self.click(AppListLoc.CREATE_APP_LOC)

    def enter_app_name(self, app_name: str):
        self.fill(AppListLoc.APP_NAME_LOC, app_name)

    def enter_app_desc(self, app_desc: str):
        self.fill(AppListLoc.APP_DESC_LOC, app_desc)

    def click_primary_button(self):
        self.click(AppListLoc.PRIMARY_BTN)
