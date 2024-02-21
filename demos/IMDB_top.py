from playwright.sync_api import sync_playwright


def run() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        try:
            base_url = "http://imdb.kxapps.com/default.aspx?page="
            page.goto(base_url)
            page.wait_for_load_state("networkidle")
            print(page.title())

            total_pages = int(page.locator('a.on').count() + page.locator('a.num').count())

            for page_number in range(1, total_pages + 1):
                page.goto(base_url + str(page_number))

                titles = page.locator('h2 > a').all()
                points = page.locator('.mov_point > b').all()

                for t, p in zip(titles, points):
                    title = t.inner_text()
                    point = p.get_attribute('title')
                    print(title, point)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            page.close()


if __name__ == "__main__":
    run()
