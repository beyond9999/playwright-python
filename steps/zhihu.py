from behave import given, when, then
from playwright.sync_api import sync_playwright

from demos.get_zhihu_billboard import WebScraper


@given('我启动网络爬虫')
def step_initialize_web_scraper(context):
    with sync_playwright() as p:
        context.scraper = WebScraper(p)


@when('我爬取"{url}"的信息')
def step_scrape_information(context, url):
    context.scraper.scrape_information(url)


@then('我应该获取到热榜条目和它们的评论')
def step_verify_hot_list_and_comments(context):
    # 可以添加逻辑来验证获取的数据，例如检查是否成功获取热榜条目和评论
    pass