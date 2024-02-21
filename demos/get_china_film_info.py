import os
import wget
import time
from playwright.sync_api import sync_playwright


def run() -> None:
    start_time = time.time()
    p = sync_playwright().start()
    browser = p.webkit.launch(headless=True)
    context = browser.new_context(no_viewport=True)
    page = context.new_page()

    with open(r"./stealth.min.js") as f:
        page.add_init_script(f.read())

    page.goto('https://cfc.com.cn/movies')

    try:
        page.wait_for_selector("//a/span[text()='电影']").click()
        page.locator(".tab-item >> text='正在热映'").click()
        page.wait_for_load_state()

        names = page.locator('.film-name').all()
        images = page.locator('.el-image__inner').all()
        buttons = page.locator('.ticket-sell').all()

        with open(f"./datas/{page.title()}.txt", "w", encoding="utf-8") as file:
            for n, im, b in zip(names, images, buttons):
                name = n.inner_text()
                image_url = im.get_attribute('src').split('_')[0].strip()
                print(f"电影名称：《{name}》\n电影封面：{image_url}")
                file.write(f"电影名称：《{name}》\n电影封面：{image_url}\n")

                # ext = '.jpg' if '.jpg' in image_url else '.png'
                # wget.download(image_url, os.path.join("./datas/", f"{name}{ext}"))

                b.click()
                page.wait_for_selector('.film-info-item')
                film_info = page.locator('.film-info-item').all()

                for i in film_info:
                    print(i.inner_text())
                    file.write(i.inner_text() + "\n")
                file.write("-----------------\n")
                page.go_back()

        end_time = time.time()
        print(f"脚本执行耗时 {end_time - start_time:.3f} 秒")
    except Exception as e:
        raise e
    finally:
        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
