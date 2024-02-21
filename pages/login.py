from common.base import BasePage
from pages_element.login_element import LoginLoc


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

    def enter_username(self, username: str):
        self.fill(LoginLoc.USERNAME_LOC, username)

    def enter_password(self, password: str):
        self.fill(LoginLoc.PASSWORD_LOC, password)

    def click_login_button(self):
        self.click(LoginLoc.LOGIN_BTN)
