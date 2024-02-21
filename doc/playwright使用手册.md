一、playwright介绍
playwright是一个自动化测试工具，由微软开发，主要用于web端的UI测试，支持Python、Java，下文中介绍的playwright均指playwright-python。Playwright是一个强大的Python库，仅用一个API即可自动执行Chromium、Firefox、WebKit等主流浏览器自动化操作，并同时支持以无头模式、有头模式运行。Playwright提供的自动化技术是绿色的、功能强大、可靠且快速，支持Linux、Mac以及Windows操作系统。

playwright相比已有的自动化测试框架来说，具有有很多优势，比如：

跨浏览器，支持Chromium、Firefox、WebKit
跨操作系统，支持Linux、Mac、Windows
可提供录制生成代码功能，解放双手
可用于移动端

二、安装
1、安装playwright库
pip install playwright    #python版本要求：3.7+以上

2、安装浏览器驱动文件
python -m playwright install	#因为安装驱动是去外网下载，所以下载的时候会有点慢

三、基本使用方法
1、录制脚本
输入以下命令，pythonwright会使用谷歌浏览器打开百度并且录制脚本，保存为test.py

python -m playwright codegen --target python -o test.py -b chromium https://www.baidu.com
--target：规定生成脚本的语言，有JS和Python两种，默认为Python
-o：将录制的脚本保存到一个文件
-b：指定浏览器驱动

2、定位方式
1)xpath
选择器以//或..假定为xpath=selector
示例：page.click('xpath=//html')

简写方式：page.click('//html')

2)text
选择器以引号（"或'）开头和结尾为text=selector
示例：page.click('text="foo"')

简写方式：page.click('"foo"')

3)css
否则，假设选择器为 css=selector
示例：page.click('css=div')

简写方式：page.click('div')

四、使用方法
1、添加cookie--addCookies
with sync_playwright() as p:
    browser_type = p.chromium
    browser = browser_type.launch(headless=False)
    context = browser.newContext()
    context.addCookies(cookies=[{'name': 'xx','value':'xx','path':'xx','domain':'xx'},
    							{'name': 'xx','value':'xx','path':'xx','domain':'xx'}]
    page1 = context.newPage()

2、跳转网址--goto
page1页面进入指定网址
page1.goto('xx')

3、寻找元素--querySelector
寻找page1页面上的元素，如果没有找到，返回null
page1.querySelector('xx')

4、点击链接跳转新页面
点击网页1的链接跳转到网页2后，定位网页2
with page1.expect_popup() as popup_info:
page1.click('xx')  # 此处点击A页面跳转链接
page2 = popup_info.value
page2.click('xx')  # B页面的其他操作
page2.fill('xx', 'str')

5、点击元素--click
page1.click('xx')

6、填充元素--fill
page1.fill('xx','xx')

7、智能等待API
element_handle.is_checked()
element_handle.is_disabled()
element_handle.is_editable()
element_handle.is_enabled()
element_handle.is_hidden()
element_handle.is_visible()
page.is_checked(selector, **kwargs)
page.is_disabled(selector, **kwargs)
page.is_editable(selector, **kwargs)
page.is_enabled(selector, **kwargs)
page.is_hidden(selector, **kwargs)
page.is_visible(selector, **kwargs)
locator.is_checked(**kwargs)
locator.is_disabled(**kwargs)
locator.is_editable(**kwargs)
locator.is_enabled(**kwargs)
locator.is_hidden(**kwargs)
locator.is_visible(**kwargs)

8、断言options
expect(locator).not_to_be_checked(**kwargs)
expect(locator).not_to_be_disabled(**kwargs)
expect(locator).not_to_be_editable(**kwargs)
expect(locator).not_to_be_empty(**kwargs)
expect(locator).not_to_be_enabled(**kwargs)
expect(locator).not_to_be_focused(**kwargs)
expect(locator).not_to_be_hidden(**kwargs)
expect(locator).not_to_be_visible(**kwargs)
expect(locator).not_to_contain_text(expected, **kwargs)
expect(locator).not_to_have_attribute(name, value, **kwargs)
expect(locator).not_to_have_class(expected, **kwargs)
expect(locator).not_to_have_count(count, **kwargs)
expect(locator).not_to_have_css(name, value, **kwargs)
expect(locator).not_to_have_id(id, **kwargs)
expect(locator).not_to_have_js_property(name, value, **kwargs)
expect(locator).not_to_have_text(expected, **kwargs)
expect(locator).not_to_have_value(value, **kwargs)
expect(locator).not_to_have_values(values, **kwargs)
expect(locator).to_be_checked(**kwargs)
expect(locator).to_be_disabled(**kwargs)
expect(locator).to_be_editable(**kwargs)
expect(locator).to_be_empty(**kwargs)
expect(locator).to_be_enabled(**kwargs)
expect(locator).to_be_focused(**kwargs)
expect(locator).to_be_hidden(**kwargs)
expect(locator).to_be_visible(**kwargs)
expect(locator).to_contain_text(expected, **kwargs)
expect(locator).to_have_attribute(name, value, **kwargs)
expect(locator).to_have_class(expected, **kwargs)
expect(locator).to_have_count(count, **kwargs)
expect(locator).to_have_css(name, value, **kwargs)
expect(locator).to_have_id(id, **kwargs)
expect(locator).to_have_js_property(name, value, **kwargs)
expect(locator).to_have_text(expected, **kwargs)
expect(locator).to_have_value(value, **kwargs)
expect(locator).to_have_values(values, **kwargs)
expect(page).not_to_have_title(title_or_reg_exp, **kwargs)
expect(page).not_to_have_url(url_or_reg_exp, **kwargs)
expect(page).to_have_title(title_or_reg_exp, **kwargs)
expect(page).to_have_url(url_or_reg_exp, **kwargs)
expect(api_response).not_to_be_ok()
expect(api_response).to_be_ok()