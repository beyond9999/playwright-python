import time
import allure
import pytest
from playwright.sync_api import expect
from utils.read_excel import ExcelDataReader
from pages_element.app_list_element import AppListLoc
from pages_action.create_app import AppListAction as Action


class TestAppPage:

    @allure.title("创建应用失败")
    @pytest.mark.usefixtures('click_create')
    def test_create_app_fail(self, page, create_app_params):
        app_name = create_app_params['app_name']
        app_desc = create_app_params['app_desc']
        expected = create_app_params['expect']
        Action(page).create_app(page, app_name, app_desc)
        with allure.step("[断言] 创建应用失败提示文案匹配"):
            expect(page.locator(AppListLoc.FAILED_LOC)).to_have_text(expected)

    @pytest.mark.smoke
    @allure.title("创建应用成功")
    @pytest.mark.parametrize("app_name, app_desc, app_info_name",
                             ExcelDataReader("./datas/test_datas.xlsx", "创建应用").read_data())
    @pytest.mark.usefixtures('click_create')
    def test_create_app_success(self, page, app_name, app_desc, app_info_name):
        Action(page).create_app(page, f"{app_name}{time.strftime('%Y%m%d%H%M%S')}", app_desc)
        with allure.step("[断言] 创建应用成功"):
            expect(page.locator(app_info_name)).to_be_visible()
