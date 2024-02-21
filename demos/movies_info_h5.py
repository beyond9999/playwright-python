import os
import wget
from playwright.sync_api import sync_playwright


def run() -> None:
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        **{
            "viewport": {"width": 400, "height": 700},
            "user_agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            ),
            "no_viewport": False
        }
    )
    page = context.new_page()
    with open(r"./stealth.min.js") as f:
        page.add_init_script(f.read())
    page.goto("https://mini.cfc.com.cn/#/home")

    try:
        page.wait_for_selector("//span[text()='电影']").click()
        page.wait_for_timeout(1000)
        items = page.locator('div.film-content.min')

        with open(f"./datas/{page.title()}.txt", "w", encoding="utf-8") as file:
            for i in range(items.count()):
                film_name = items.nth(i).locator('.film-name span').inner_text()
                status = items.nth(i).locator('.btn').inner_text()
                print(f"电影名称：{film_name}\n状态：{status}")
                file.write(f"电影名称：《{film_name}》\n状态：【{status}】\n")

                items.nth(i).locator('.film-image').click()
                page.wait_for_timeout(1000)

                video = page.locator('.headVideo > video')
                if video.is_visible(timeout=3000):
                    link = video.get_attribute("src")
                    print(f"影片预览链接：{link}")
                    file.write(f"影片预览链接：{link}\n-----------------\n")
                    wget.download(link, os.path.join("./datas/", f"{film_name}.mp4"))
                else:
                    print(f"未找到{film_name}视频元素")
                    file.write("该影片无预览视频\n-----------------\n")

                page.go_back()
    except Exception as e:
        raise e
    finally:
        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    run()
