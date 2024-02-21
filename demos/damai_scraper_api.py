import requests

headers = {
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


def get_info():
    url = 'https://search.damai.cn/searchajax.html'
    response = requests.get(url, headers=headers)
    data = response.json()
    city_names = [city['name'] for city in data['pageData']['factMap']['cityname']]
    print("城市(cty):", city_names)
    category_names = [c['name'] for c in data['pageData']['factMap']['categoryname']]
    print("分类(ctl):", category_names)
    sub_names = [s['name'] for s in data['pageData']['factMap']['subcategoryname']]
    print("子类(sctl):", sub_names)
    print("时间(tsg): 0 [全部]  1[今天]  2[明天]  3[本周末]  4[一个月内]")


def get_response(cty, ctl, tsg):
    currPage = 1
    total_pages = 1

    while currPage <= total_pages:
        url = f'https://search.damai.cn/searchajax.html?keyword=&cty={cty}&ctl={ctl}&sctl=&tsg={tsg}&st=&et=&order=2' \
              f'&pageSize=30&currPage={currPage} '
        response = requests.get(url, headers=headers)
        data = response.json()
        total_pages = data['pageData']['totalPage']
        print("总数：", data['pageData']['totalResults'])
        print("总页数：", total_pages)

        for i in data['pageData']['resultData']:
            print(f"[{i['categoryname']}] [{i['cityname']}]", i['name'], f"价格：{i['price_str']}", i['showtime'],
                  i['venue'], i['actors'])
            extracted_id = i['id'].split('_')[2]
            print(f"https://detail.damai.cn/item.htm?id={extracted_id}")
            print("-----------------------------------------------")

        currPage += 1


if __name__ == "__main__":
    get_info()
    cty_input = input("请输入城市: ")
    ctl_input = input("请输入分类: ")
    tsg_input = int(input("请输入时间: "))
    get_response(cty_input, ctl_input, tsg_input)
