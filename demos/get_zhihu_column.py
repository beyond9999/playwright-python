import os
import re
import fake_useragent
from playwright.sync_api import sync_playwright


class WebScraper:
    def __init__(self, playwright):
        self.p = playwright
        self.browser = self.p.chromium.launch(headless=True)
        self.page = self.setup_context()

    def setup_context(self):
        context = self.browser.new_context(no_viewport=True, user_agent=fake_useragent.UserAgent().random)
        page = context.new_page()
        page.route(re.compile(r"\.(png|jpg|svg)|https://pic"), lambda route: route.abort())
        return page

    def scrape_information(self):
        try:
            self.page.goto('https://www.zhihu.com/column/xuehy')
            total = int(self.page.locator('div.css-1symrae').inner_text().strip())
            print(f"本专栏总数为：{total}")

            output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{self.page.title()}.txt")

            with open(output_file_path, 'w', encoding='utf-8') as file:
                while True:
                    self.page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
                    self.page.evaluate('window.scrollTo(0, 0);')
                    count = int(self.page.locator('h2 > span > a').count())
                    if count > 100:
                        print(f"获取到的专栏数为：{count}")
                        break

                title_elements = self.page.locator('h2 > span > a').all()
                for title in title_elements:
                    format_title = f'{title.inner_text()}'
                    link = f"https:{title.get_attribute('href')}"
                    print(f"{format_title} {link}\n")
                    file.write(f"{format_title} {link}\n")

                    page = self.page.context.new_page()
                    page.route(re.compile(r"\.(png|jpg|svg)|https://pic"), lambda route: route.abort())
                    page.goto(f"https:{title.get_attribute('href')}")

                    if page.is_visible('.signFlowModal > button'):
                        page.locator('.signFlowModal > button').click()

                    comments = page.locator('div.Post-RichTextContainer p').all()
                    for comment in comments:
                        comment_text = comment.inner_text().strip()
                        if comment_text:
                            file.write(comment_text + '\n')
                    file.write('=================================\n')
                    page.close()

        except Exception as e:
            print(f"运行过程中发生错误 >>> {e}")


if __name__ == "__main__":
    with sync_playwright() as p:
        scraper = WebScraper(p)
        scraper.scrape_information()
