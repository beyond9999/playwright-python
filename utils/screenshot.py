import os
import time
import allure
from playwright.sync_api import Page


def allure_attach_screenshot(page: Page, selector=None, full_page=False):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(base_path, 'outputs', 'screenshots')
    os.makedirs(folder, exist_ok=True)

    now_time = time.strftime('%Y-%m-%d-%H_%M_%S')
    milliseconds = str(time.time()).replace('.', '')[-3:]
    name = f"{now_time}_{milliseconds}.png"
    file_path = os.path.join(folder, name)

    if selector:
        element = page.locator(selector)
        element.screenshot(path=file_path)
    elif full_page:
        page.screenshot(path=file_path, full_page=True)
    else:
        page.screenshot(path=file_path)

    allure.attach.file(file_path, name=name, attachment_type=allure.attachment_type.PNG)
