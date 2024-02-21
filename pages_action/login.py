import allure
from pages.login import LoginPage


class LoginAction(LoginPage):

    def login(self, page, username, password):
        login_page = LoginPage(page)

        with allure.step("输入用户名"):
            login_page.enter_username(username)
        with allure.step("输入密码"):
            login_page.enter_password(password)
        with allure.step("点击登录按钮"):
            login_page.click_login_button()
