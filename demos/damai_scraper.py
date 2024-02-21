import requests
import pandas as pd
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style

HEADERS = {
    'authority': 'search.damai.cn',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'referer': 'https://search.damai.cn/search.htm?spm=a2oeg.home.top.dcategory.a7e923e1QI5eB3&order=1',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 '
                  'Safari/537.36',
    'x-xsrf-token': 'edc507e9-8e45-4a56-bc9d-b856388d8c7f'
}


class DamaiInfoScraper:
    def __init__(self, root, url=None, time_options=None):
        self.root = root
        self.url = url or 'https://search.damai.cn/searchajax.html'
        self.time_options = time_options or {'全部': 0, '今天': 1, '明天': 2, '本周末': 3, '一个月内': 4}
        self.setup_gui()

    def setup_gui(self):
        data = self.fetch_data()
        if data:
            city_data = [city['name'] for city in data['pageData']['factMap']['cityname']]
            ctl_data = [category['name'] for category in data['pageData']['factMap']['categoryname']]

            self.city_var = tk.StringVar(value=city_data[0])
            self.ctl_var = tk.StringVar(value=ctl_data[0])
            self.time_var = tk.StringVar(value=list(self.time_options.keys())[0])

            style = Style(theme='flatly')
            style.configure('.', font=('Helvetica', 11))
            search_button = ttk.Button(self.root, text="搜索", command=self.get_response)
            ttk.Label(self.root, text="城市").grid(row=0, column=0, padx=10, pady=10)
            ttk.Combobox(self.root, textvariable=self.city_var, values=city_data).grid(row=0, column=1, padx=10, pady=10)
            ttk.Label(self.root, text="风格").grid(row=1, column=0, padx=10, pady=10)
            ttk.Combobox(self.root, textvariable=self.ctl_var, values=ctl_data).grid(row=1, column=1, padx=10, pady=10)
            ttk.Label(self.root, text="日期").grid(row=2, column=0, padx=10, pady=10)
            ttk.Combobox(self.root, textvariable=self.time_var, values=list(self.time_options.keys())).grid(row=2, column=1, padx=10, pady=10)
            search_button.grid(row=3, column=1, pady=10, sticky="ew")

    def fetch_data(self):
        try:
            response = requests.get(self.url, headers=HEADERS)
            data = response.json()
            return data
        except Exception as e:
            print(f"获取数据时发生错误：{e}")
            return None

    def get_response(self):
        city_input = self.city_var.get()
        ctl_input = self.ctl_var.get()
        time_input = self.time_options[self.time_var.get()]
        curr_page = 1
        total_pages = 1
        data_list = []

        try:
            while curr_page <= total_pages:
                url = f'{self.url}?keyword=&cty={city_input}&ctl={ctl_input}&sctl=&' \
                      f'tsg={time_input}&st=&et=&order=2&pageSize=30&currPage={curr_page}'
                response = requests.get(url, headers=HEADERS)
                data = response.json()
                total_pages = int(data['pageData']['totalPage'])
                if 'resultData' in data['pageData']:
                    for item in data['pageData']['resultData']:
                        self.print_and_append_data(item, data_list)
                else:
                    print("未找到活动数据。")
                curr_page += 1
            self.save_to_excel(city_input, ctl_input, data_list)
        except KeyError:
            print("错误：无法获取活动数据，请检查您的输入并重试。")
        except Exception as e:
            print(f"发生错误：{e}")

    def print_and_append_data(self, item, data_list):
        print(f"【{item['categoryname']}】 【{item['cityname']}】 {item['name']} [价格]：{item['price_str']} "
              f"[时间]：{item['showtime']} [场地]：{item['venue']} {item['actors']}\n"
              f"https://detail.damai.cn/item.htm?id={item['id'].split('_')[2]}\n"
              f"-----------------------------------------------")
        artist_name = item['actors'].split('：')[-1] if item['actors'] else ''
        data_list.append({
            '活动名称': item['name'],
            '价格': item['price_str'],
            '日期': item['showtime'],
            '场地': item['venue'],
            '艺人': artist_name,
            '购票链接': f"https://detail.damai.cn/item.htm?id={item['id'].split('_')[2]}"
        })

    def save_to_excel(self, city, ctl, data_list):
        df = pd.DataFrame(data_list)
        sheet_name = f'大麦_{city}_{ctl}.xlsx'
        df.to_excel('./datas/' + sheet_name, index=False)
        print(f"数据已保存到文件: {sheet_name}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Search DaMai Info")
    root.geometry("300x200")
    scraper = DamaiInfoScraper(root)
    root.mainloop()
