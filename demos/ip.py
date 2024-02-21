import time
from playwright.sync_api import sync_playwright  # 导入playwright同步api


def run(playwright):  # 定义run方法
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()  # 创建context对象，context之间是相互隔离的，可以理解为轻量级的浏览器实例

    page = context.new_page()  # 创建page对象，真正打开浏览器界面
    url = "http://httpbin.org/ip"
    page.goto(url, timeout=120000)
    time.sleep(6)
    for i in range(1, 10):
        # input("输入continue")
        print("***", page.content())
        time.sleep(10)
        page.goto(url, timeout=120000)
        # page.reload(timeout=120000)


if __name__ == '__main__':
    with sync_playwright() as playwright:  # playwright使用入口，通过上下文方式
        run(playwright)  # 调用run方法，将playwright实例传入
