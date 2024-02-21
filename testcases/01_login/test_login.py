import allure
import pytest
from playwright.sync_api import expect
from utils.read_excel import ExcelDataReader
from pages_element.login_element import LoginLoc
from pages_action.login import LoginAction as Action


class TestLoginPage:
    @allure.title("用户登录失败")
    def test_login_fail(self, page, invalid_login_params):
        username = invalid_login_params['usr']
        password = invalid_login_params['pwd']
        expected = invalid_login_params['expect']
        Action(page).login(page, username, password)
        with allure.step("[断言] 登录失败提示文案匹配"):
            expect(page.locator(LoginLoc.FAILED_TEXT)).to_have_text(expected)

    @pytest.mark.smoke
    @allure.title("用户登录成功")
    @pytest.mark.parametrize("username, password, expect_loc",
                             ExcelDataReader("./datas/test_datas.xlsx", "登录").read_data())
    def test_login_success(self, page, username, password, expect_loc):
        Action(page).login(page, username, password)
        with allure.step("[断言] 登录成功"):
            expect(page.locator(expect_loc)).to_be_visible()

    @allure.title("chromium登录")
    def test_chromium_login(self, page, login_params):
        if 'chromium_usr' in login_params:
            username = login_params['chromium_usr']
            password = login_params['chromium_pwd']
            expected = login_params['chromium_expect']

            Action(page).login(page, username, password)
            with allure.step("断言"):
                expect(page.locator(expected)).to_be_visible()

    @allure.title("firefox登录")
    def test_firefox_login(self, page, login_params):
        if 'firefox_usr' in login_params:
            username = login_params['firefox_usr']
            password = login_params['firefox_pwd']
            expected = login_params['firefox_expect']

            Action(page).login(page, username, password)
            with allure.step("断言"):
                expect(page.locator(expected)).to_be_visible()

    @allure.title("webkit登录")
    def test_webkit_login(self, page, login_params):
        if 'webkit_usr' in login_params:
            username = login_params['webkit_usr']
            password = login_params['webkit_pwd']
            expected = login_params['webkit_expect']

            Action(page).login(page, username, password)
            with allure.step("断言"):
                expect(page.locator(expected)).to_be_visible()
