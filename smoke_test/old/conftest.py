import pytest
from common.base import BasePage


@pytest.fixture
def p(page):
    return BasePage(page)


@pytest.fixture
def switch_tab(p):
    p.wait(1)
    while True:
        if len(p.switch_tab(-1).context.pages) > 1:
            p.wait(1)
            if p.switch_tab(-1).title() != "飞速低代码":
                p.wait(1)
                p.switch_tab(-1)
                break


@pytest.fixture
def close_tab(p, switch_tab):
    p.right_click("//fly-stage//fly-stage-bar[1]")
    p.left_click("span >> text='关闭所有页签'")


@pytest.fixture
def open_attr(p):
    yield
    [p.click("//tr[16]/td[7]") for _ in range(2)]
