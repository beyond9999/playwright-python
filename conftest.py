# -*- encoding=utf8 -*-
__author__ = "blues_chen"

import os
import re
import time
import allure
import pytest
from utils.logger import log
from utils.read_config import *
from playwright.sync_api import sync_playwright


# 添加自定义命令行选项
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="test",
        choices=["test", "prod"],
        help="指定测试环境 ('test', 'prod')"
    )

    parser.addoption(
        "--browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="指定浏览器类型 (chromium, firefox, webkit)"
    )

    parser.addoption(
        "--headless",
        action="store",
        default="false",
        help="指定无头浏览器 (True, False)"
    )

    parser.addoption(
        "--init_js",
        action="store",
        default="false",
        help="指定初始化 JS (True, False)"
    )


# 监听页面请求事件
def on_request(request):
    log.info(
        f"[请求方法]: {request.method}\n"
        f"[请求url]：{request.url}\n"
        f"[请求头]：{request.headers}\n"
        f"[请求体]：{request.post_data}\n"
        f"============================="
    )


# 监听页面返回事件
def on_response(response):
    status_code = response.status
    url = response.url
    headers = response.headers
    response_text = response.text()

    message_types = {
        range(100, 103): "消息",
        range(200, 208): "成功",
        range(300, 308): "重定向",
        range(400, 452): "请求错误",
        range(500, 601): "服务端错误",
    }

    for status_range, message_type in message_types.items():
        if status_code in status_range:
            if message_type in ("消息", "成功"):
                log_level = log.info
            elif message_type == "重定向":
                log_level = log.warning
            else:
                log_level = log.error

            log_message = (
                f"[{message_type}]\n"
                f"[状态码]：{status_code}\n"
                f"[响应url]：{url}\n"
                f"[响应头]：{headers}\n"
                f"[响应内容]：{response_text}\n"
                f"==========================="
            )
            log_level(log_message)
            break


# 关闭Webdriver属性
def _init_js(page):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, "stealth.min.js")

    with open(file_path) as f:
        js_file = f.read()
        page.add_init_script(js_file)
        return page


@pytest.fixture(scope="session")
def context(request):
    browser_type = str(request.config.getoption("--browser"))
    headless = request.config.getoption("--headless").lower() == "true"

    p = sync_playwright().start()
    browser = getattr(p, browser_type).launch(headless=headless, args=['--start-maximized'])
    context = browser.new_context(no_viewport=True)
    # context.tracing.start(screenshots=True, snapshots=True, sources=True)  # 在创建/导航页面之前开始跟踪

    yield context
    # context.tracing.stop(path="trace.zip")      # 停止跟踪并将其导出到zip存档中
    # 使用 Playwright CLI 或在浏览器中打开保存的跟踪   playwright show-trace trace.zip
    # URL 打开远程跟踪    playwright show-trace https://example.com/trace.zip
    context.close()
    browser.close()


# pytest path --env=test --browser=chromium --headless=True --init_js=True
@pytest.fixture(scope="session")
def page(request, context):
    page = context.new_page()
    # init_js = request.config.getoption("--init_js").lower() == "true"
    # if init_js is True:
    #     page = _init_js(page)

    yield page
    page.close()


# 获取环境配置
@pytest.fixture(scope="session")
def env(request):
    env = request.config.getoption("--env")
    try:
        return read_cfg()["URL"][env]
    except KeyError:
        raise ValueError(f"无效的环境 '{env}'")


def cancel_request(route):
    route.abort()


# 打开测试页面
@pytest.fixture(scope="session", autouse=True)
def open_page(page, env):
    # page.route(re.compile(r"\.(png|jpg|svg)"), cancel_request)
    # page.on("request", lambda request: on_request(request))
    # page.on("response", lambda response: on_response(response))
    page.goto(env)


# 自定义pytest钩子函数，用于在测试用例失败时捕获屏幕截图
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    if call.when == "call" and call.excinfo is not None:
        if item.funcargs.get("page"):
            page = item.funcargs["page"]
            screenshot = page.screenshot()
            allure.attach(
                name="Failure Screenshot",
                body=screenshot,
                attachment_type=allure.attachment_type.PNG,
            )


# 收集测试结果
def pytest_terminal_summary(terminalreporter):
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    log.info(f"用例总数: {_TOTAL}")
    log.info(f"通过用例数: {_PASSED}")
    log.error(f"异常用例数: {_ERROR}")
    log.error(f"失败用例数: {_FAILED}")
    log.warning(f"跳过用例数: {_SKIPPED}")
    log.info("用例执行时长: %.2f" % _TIMES + " s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        log.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        log.info("用例成功率: 0.00 %")

# def pytest_collection_modifyitems(session, items):
#     # 测试项的执行顺序会变为随机顺序
#     print('items 类型:', type(items))
#     print('session 类型:', type(session))
#     print("收集到的测试用例：")
#     random.shuffle(items)
