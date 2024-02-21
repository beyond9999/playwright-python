import allure
from pages.app_list import AppListPage


class AppListAction(AppListPage):

    def click_create_app(self, page):
        app_list_page = AppListPage(page)
        with allure.step("点击页面右上角'新建应用'按钮"):
            app_list_page.click_create_app_button()

    def create_app(self, page, app_name, app_desc):
        app_list_page = AppListPage(page)
        with allure.step("输入应用名称"):
            app_list_page.enter_app_name(app_name)
        with allure.step("输入应用描述"):
            app_list_page.enter_app_desc(app_desc)
        with allure.step("点击'确定'按钮"):
            app_list_page.click_primary_button()
