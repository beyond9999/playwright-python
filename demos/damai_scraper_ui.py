import os
import re
import openpyxl
from playwright.sync_api import sync_playwright


def run() -> None:
    browser = sync_playwright().start().chromium.launch(headless=True, args=['--start-maximized'])
    context = browser.new_context(no_viewport=True)
    page = context.new_page()

    page.route(re.compile(r"\.(png|jpg|svg)"), lambda route: route.abort())
    with open(r"./stealth.min.js") as f:
        page.add_init_script(f.read())

    page.goto("https://search.damai.cn/search.htm")
    page.wait_for_load_state("networkidle")

    # 滑块验证码处理
    lock = page.locator('#nc_1__scale_text')
    btn = page.locator('.nc_iconfont btn_slide')
    if lock.is_visible():
        lock_bbox = lock.bounding_box()
        lock_length = lock_bbox['width']
        btn_bbox = btn.bounding_box()
        page.mouse.move(btn_bbox['x'], btn_bbox['y'])
        page.mouse.down()
        page.mouse.move(btn_bbox['x'] + lock_length, btn_bbox['y'], steps=10)  # 可以调整steps以控制平移速度
        page.mouse.up()

    factor = page.locator('.factor-item')
    page.locator('.factor-more').click()

    titles = []
    for i in range(len(factor.all())):
        title = factor.nth(i).locator('.factor-title').inner_text()
        content_items = factor.nth(i).locator('.factor-content-item').all_inner_texts()
        content_items = [item for item in content_items if item != '全部']
        if i != 2:
            if content_items:
                titles.append(title)
                print(f"{title} {content_items}")

    file_name = input("请输入保存Excel的文件名: ")
    inputs = [input(f"{title}") for title in titles]
    for title, input_value in zip(titles, inputs):
        if input_value:
            factor.get_by_text(input_value).click()

    page.locator('.search-sort_fl > span').nth(2).click()
    page.wait_for_timeout(2000)

    # 创建一个新的Excel工作簿
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    # 添加表头行
    sheet.append(["分类", "城市", "项目名称", "艺术家/地址/时间", "价格", "购票链接"])
    page.wait_for_timeout(2000)

    while True:
        items_tag = page.locator('.items__img__tag').all()
        items_city = page.locator('.items__txt__title > span').all()
        items_title = page.locator('.items__txt__title > a').all()
        items_artist = page.locator('.items__txt div:nth-child(2)').all()
        items_address = page.locator('.items__txt div:nth-child(3)').all()
        items_time = page.locator('.items__txt div:nth-child(4)').all()
        items_price = page.locator('.items__txt__price > span').all()

        for tag, city, title, price, artist, addr, time in zip(items_tag, items_city, items_title, items_price,
                                                               items_artist, items_address, items_time):
            href = title.get_attribute('href')
            href_parts = href.split('&clicktitle=')
            if len(href_parts) > 1:
                href = href_parts[0]

            print(
                f"【{tag.inner_text()}】 {city.inner_text()} {title.inner_text()} {price.inner_text()}| "
                f"{artist.inner_text()} | {addr.inner_text()} | {time.inner_text()}\n"
                f"https:{href}"
            )

            sheet.append(
                [
                    tag.inner_text(), city.inner_text(), title.inner_text(),
                    f"{artist.inner_text()}  {addr.inner_text()}  {time.inner_text()}",
                    price.inner_text(), f"https:{href}"
                ]
            )

        next_btn = page.locator('a.sort__next')
        min_num, max_num = [int(span.inner_text()) for span in page.locator('.sort__num > span').all()]
        if min_num < max_num:
            next_btn.click()
            page.wait_for_timeout(2000)
        else:
            print(page.locator('.search-box-top').inner_text())
            break

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name + ".xlsx")
    workbook.save(file_path)

    page.close()


if __name__ == "__main__":
    run()
