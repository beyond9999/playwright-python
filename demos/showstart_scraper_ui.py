import os
import re
import openpyxl
import tkinter as tk
from tkinter import ttk
from playwright.sync_api import sync_playwright
import fake_useragent

URL = "https://www.showstart.com/event/list?pageSize=88888"


class ShowStartScraper:
    def __init__(self):
        self.cities = []
        self.times = []
        self.styles = []

    def fetch_texts(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(user_agent=fake_useragent.UserAgent().random)
            page = context.new_page()
            page.route(re.compile(r"\.(png|jpg|svg)"), lambda route: route.abort())
            page.goto(URL)

            self.cities, self.times, self.styles = self._get_texts(page)

    def _get_texts(self, page):
        indexes = [0, 2, 3]
        texts = []
        for index in indexes:
            elements = page.locator('.tags').nth(index).locator('span').all_text_contents()
            texts.append(elements)

        filter_box = page.locator('.filter-box')
        labels = [filter_box.locator('label').nth(i).inner_text() for i in indexes]
        print("_".join(labels))

        cities, times, styles = texts
        return cities, times, styles

    def fetch_page_data(self, page, criteria, filter_sort):
        for criterion in criteria:
            item_locator = f'.filter-box span >> text="{criterion}"'
            elements = page.locator(item_locator).all()
            for element in elements:
                element.click()
                page.wait_for_timeout(1000)

        sorts = page.locator('.filter-box div:nth-child(4) span').all()

        for sort in sorts:
            if sort.text_content() == filter_sort:
                sort.click()
                sort_name = sort.text_content()
                print(f">>> 开始获取演出信息 >>>")
                print("--------------------------------------------------")
                page.wait_for_timeout(1000)

                return sort_name

    def extract_show_items(self, page, sort_name, workbook, sheet):
        total_items = 0
        while True:
            show_items = page.locator('//a[contains(@class, "show-item")]').all()
            total_items += len(show_items)
            page.wait_for_timeout(1000)

            if not show_items:
                print("未找到相关项目")
                break

            for t, a, p, ti, ad, tick in zip(
                    page.locator('.list-box .title').all(), page.locator('.list-box .artist').all(),
                    page.locator('.price > span').all(), page.locator('.list-box .time').all(),
                    page.locator('.list-box .addr').all(),
                    page.locator('//a[contains(@class, "show-item")]').all()
            ):
                match = re.match(r'\[.*?](.*?)$', ad.text_content())
                ad_content = match.group(1).strip() if match else ad.text_content()
                sheet.append(
                    [
                        t.text_content(), a.text_content().split('：')[1].strip(),
                        p.text_content().split('¥')[1].strip(), ti.text_content().split('：')[1].strip(),
                        ad_content, f"https://www.showstart.com{tick.get_attribute('href')}"
                    ]
                )

                print(f"【{sort_name}】:{t.text_content()} | {a.text_content()} | "
                      f"价格：{p.text_content()} | {ti.text_content()} | 地址：{ad.text_content()}\n"
                      f"【购票链接】：https://www.showstart.com{tick.get_attribute('href')}\n"
                      f"----------------------------------------------")

            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            if page.locator('button.btn-next').is_enabled():
                page.locator('button.btn-next').click()
            else:
                page.evaluate("window.scrollTo(0, 0);")
                print(f"【{sort_name}】类型项目的总计为：{total_items}")
                break

    def save_to_excel(self, workbook, filename):
        workbook.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename + ".xlsx"))

    def start_gui(self):
        self.fetch_texts()

        root = tk.Tk()
        root.title("ShowStart Perform")
        root.geometry("300x320")

        city_label = ttk.Label(root, text="城市")
        city_entry = ttk.Combobox(root, values=self.cities)
        city_entry.set(self.cities[0])
        city_label.pack()
        city_entry.pack()

        venue_label = ttk.Label(root, text="场地(选填)")
        venue_entry = ttk.Entry(root)
        venue_label.pack()
        venue_entry.pack()

        time_label = ttk.Label(root, text="开演时间")
        time_entry = ttk.Combobox(root, values=self.times)
        time_entry.set(self.times[0])
        time_label.pack()
        time_entry.pack()

        filter_sort_label = ttk.Label(root, text="风格")
        filter_sort_entry = ttk.Combobox(root, values=self.styles)
        filter_sort_entry.set(self.styles[0])
        filter_sort_label.pack()
        filter_sort_entry.pack()

        excel_filename_label = ttk.Label(root, text="保存文件名")
        excel_filename_entry = ttk.Entry(root)
        excel_filename_entry.insert(0, "秀动演出信息")
        excel_filename_label.pack()
        excel_filename_entry.pack()

        def start_scraping():
            city = city_entry.get().strip()
            venue = venue_entry.get().strip()
            time = time_entry.get().strip()
            filter_sort = filter_sort_entry.get()
            excel_filename = excel_filename_entry.get()

            criteria = []
            if city:
                criteria.append(city)
            if venue:
                criteria.append(venue)
            if time:
                criteria.append(time)

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(user_agent=fake_useragent.UserAgent().random)
                page = context.new_page()
                page.route(re.compile(r"\.(png|jpg|svg)"), lambda route: route.abort())
                page.goto(URL)

                sort_name = self.fetch_page_data(page, criteria, filter_sort)
                if sort_name:
                    workbook = openpyxl.Workbook()
                    sheet = workbook.active
                    sheet.append(["项目名称", "艺术家", "价格", "演出时间", "地址", "购票链接"])

                    self.extract_show_items(page, sort_name, workbook, sheet)
                    self.save_to_excel(workbook, excel_filename)

        start_button = ttk.Button(root, text="开始获取", command=start_scraping)
        start_button.pack()

        root.mainloop()


if __name__ == "__main__":
    scraper = ShowStartScraper()
    scraper.start_gui()
