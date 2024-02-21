import re
import fake_useragent
from playwright.sync_api import sync_playwright


class WebScraper:
    def __init__(self):
        self.p = sync_playwright().start()
        self.browser = self.p.firefox.launch(headless=True)
        self.page = self.setup_page()

    def setup_page(self):
        context = self.browser.new_context(
            user_agent=fake_useragent.UserAgent().random,
            no_viewport=True
        )
        page = context.new_page()
        page.route(re.compile(r"\.(png|jpg|svg)|https://img"), lambda route: route.abort())
        return page

    def scrape_information(self, url):
        try:
            self.page.goto(url=url)
            self.page.wait_for_load_state("networkidle")
            items = self.page.locator('.kr-information-left li').all()
            for i in items:
                i.click()
                print(f'======【{i.inner_text()}】======')
                links = self.page.locator('.article-item-title').all()
                for link in links:
                    title = link.inner_text()
                    href = link.get_attribute('href')
                    print(f'{title} https://36kr.com{href}')

        except Exception as e:
            print(f"An error occurred during scraping: {str(e)}")


if __name__ == "__main__":
    WS = WebScraper()
    WS.scrape_information("https://36kr.com/information/web_news/")