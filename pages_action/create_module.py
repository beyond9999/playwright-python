import allure
from pages.app_details import AppDetailsPage


class AppDetailsAction(AppDetailsPage):

    def click_create_app(self, page):
        app_details_page = AppDetailsPage(page)
        with allure.step("点击应用"):
            app_details_page.click_app()

    def create_module(self, page, module_name):
        app_details_page = AppDetailsPage(page)
        with allure.step("点击'新建模块'"):
            app_details_page.click_create_module()
        with allure.step("点击选择后端模板"):
            app_details_page.click_backend_template()
        with allure.step("输入模块名称"):
            app_details_page.enter_module_name(module_name)
        with allure.step("点击'确定'按钮"):
            app_details_page.click_confirm_button()