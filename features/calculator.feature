Feature: 网络爬取功能

  Scenario: 获取知乎热榜信息
    Given 我启动网络爬虫
    When 我爬取"https://www.zhihu.com/billboard"的信息
    Then 我应该获取到热榜条目和它们的评论
