import os
import re
import fake_useragent
from playwright.sync_api import sync_playwright


class WebScraper:
    def __init__(self, playwright):
        self.p = playwright
        self.url = 'https://www.zhihu.com/billboard'

    def scrape_information(self):
        browser = None
        try:
            browser = self.p.chromium.launch(headless=True)
            context = browser.new_context(no_viewport=True, user_agent=fake_useragent.UserAgent().random)
            page = context.new_page()
            page.route(re.compile(r"\.(png|jpg|svg)|https://pic"), lambda route: route.abort())

            page.goto(self.url)

            index = page.locator('.HotList-itemIndex').all()
            title = page.locator('.HotList-itemTitle').all()

            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{page.title()}.txt"),
                      'w', encoding='utf-8') as file:
                for i, t in zip(index, title):
                    format_title = f'{i.inner_text()}. {t.inner_text()}'
                    print(format_title)
                    file.write(format_title + '\n')

                    i.click()
                    page.wait_for_load_state()

                    if page.is_visible('.signFlowModal > button'):
                        page.locator('.signFlowModal > button').click()

                    comments = page.locator('#QuestionAnswers-answers p').all()
                    for comment in comments:
                        file.write(comment.inner_text() + '\n')

                    file.write('=================================\n')
                    page.go_back()

        except Exception as e:
            print(f"运行过程中发生错误 >>> {e}")

        finally:
            if browser:
                browser.close()


if __name__ == "__main__":
    with sync_playwright() as p:
        scraper = WebScraper(p)
        scraper.scrape_information()
