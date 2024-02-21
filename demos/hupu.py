import re
from playwright.sync_api import sync_playwright


def run() -> None:
    def cancel_request(route):
        route.abort()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.route(re.compile(r"(.png)|(.jpg)|(.svg)"), cancel_request)
        with open(r"./stealth.min.js") as f:
            page.add_init_script(f.read())

        try:
            page.goto("https://nba.hupu.com/")
            page.wait_for_load_state("networkidle")

            links = page.locator('.list-recommend a, .list-container a').all()
            for link in links:
                title = link.inner_text()
                href = link.get_attribute('href')
                print(title, href)

            date = page.locator('.current-nba-date').inner_text()
            total = page.locator('.match-total').first.inner_text()
            print("========================================")
            print(date, total)
            print("========================================")

            matches = page.locator('.match-card[data-type="NBA常规赛"]').all()
            for match in matches:
                text = match.inner_text().strip().replace('\n', ' ').replace('数据', '')
                status = match.get_attribute('data-status')
                print(text, status)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            page.close()


if __name__ == "__main__":
    run()
