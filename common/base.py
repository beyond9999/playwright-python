from utils.logger import log
from common.decorators import timer, log_action, assert_result
from playwright.sync_api import Page, expect
from utils.screenshot import allure_attach_screenshot


# 官方文档：https://playwright.dev/python/docs/intro
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 20000
        self.load_state_timeout = 25000
        self.default_navigation_timeout = 30000

    def pause(self):
        """暂停脚本执行(仅在有界面模式启动时才有效)"""
        self.page.pause()

    def screenshot(self, selector: str = None, full_page=False):
        """截取屏幕并将其添加至allure报告中"""
        if selector:
            allure_attach_screenshot(page=self.page, selector=selector)
        elif full_page:
            allure_attach_screenshot(page=self.page, full_page=True)
        else:
            allure_attach_screenshot(page=self.page)

    def locator(self, selector: str, position: str = None, index: int = None):
        """
        查找并返回元素

        Args:
            selector (str): 元素选择器
            position (str, optional): 元素位置，可以是 "first" 或 "last"
            index (int, optional): 元素索引
        """
        element = self.page.locator(selector)

        if position == "first":
            ele = element.first
        elif position == "last":
            ele = element.last
        elif index is not None:
            ele = element.nth(index)
        else:
            ele = element

        ele.wait_for()
        ele.highlight()

        return ele

    @log_action
    def click(self, selector: str, position: str = None, index: int = None):
        """点击元素"""
        ele = self.locator(selector, position, index)
        if ele.is_enabled():
            ele.click()

        self.screenshot()

    @log_action
    def fill(self, selector: str, input_value: str, position: str = None, index: int = None):
        """输入文本"""
        ele = self.locator(selector, position, index)
        if ele.is_editable():
            ele.clear()
            ele.fill(input_value)

        self.screenshot()

    def wait(self, seconds: float):
        """强制等待"""
        self.page.wait_for_timeout(seconds * 1000)
        log.info(f">>> 等待{seconds}秒")

    def wait_page(self, state: str = "load"):
        """
        等待页面加载到特定状态

        Args:
            state (str, optional): 页面加载状态，可以是 "load"、"network"、"dom"
        """
        load_state_mapping = {
            # 等待页面完全加载
            "load": "load",
            # 等待网络空闲
            "network": "networkidle",
            # 等待 DOMContentLoaded 事件触发，即HTML文档被完全加载和解析，不包括样式表、图片和其他资源
            "dom": "domcontentloaded"
        }
        page_state = load_state_mapping.get(state)
        self.page.wait_for_load_state(state=page_state, timeout=self.load_state_timeout)
        log.info(">>> 页面已加载完成")

    def wait_navigation(self):
        """设置页面的默认导航超时时间"""
        self.page.set_default_navigation_timeout(timeout=self.default_navigation_timeout)

    def go_back(self):
        """回退到上一个页面"""
        self.page.go_back(timeout=self.load_state_timeout, wait_until="load")

    def go_forward(self):
        """前进到下一个页面"""
        self.page.go_forward(timeout=self.load_state_timeout, wait_until="load")

    def reload(self):
        """重新加载当前页面"""
        self.page.reload(timeout=self.load_state_timeout, wait_until="load")

    def wait_for_url(self, url):
        """在页面上设置一个等待，等待URL变为指定的URL"""
        self.page.wait_for_url(url)

    def page_content(self):
        """获取页面的完整HTML内容，包括文档类型"""
        self.page.content()
        log.info(self.page.content())

    def frames(self):
        """获取页面所有的iframes"""
        frames = self.page.frames
        for f in frames:
            log.info(f"获取到的frames：{f}")

    @log_action
    def find_by_frame_name(self, name: str, selector: str):
        """根据frame的name属性定位"""
        frame_ele = self.page.frame(name).locator(selector)
        return frame_ele

    def find_by_frame_id(self, selector: str, selector_or_locator: str):
        """根据frame的id属性定位"""
        frame_ele = self.page.frame_locator(selector).locator(selector_or_locator)
        return frame_ele

    @log_action
    def goto(self, url: str):
        """在当前标签页跳转到指定的URL"""
        self.page.goto(url)

    @log_action
    def new_page(self):
        """打开一个新的空白标签页"""
        self.page = self.page.context.new_page()
        return self.page

    def switch_tab(self, page_index=0):
        """根据页面索引切换标签页"""
        pages = self.page.context.pages
        log.info(f"页签总数 >>> {len(pages)}")
        for page in pages:
            log.info(f"当前页签标题 >>> {page.title()}")
        if page_index < len(pages):
            self.page = pages[page_index]
            return self.page
        else:
            log.error(f"窗口索引 {page_index} 超出范围")

    def switch_to_page(self, title=None, url=None):
        """切换到指定title或url的标签页"""
        for item_page in self.page.context.pages:
            if title:
                if title in item_page.title():
                    item_page.bring_to_front()
                    return item_page
            elif url:
                if url in item_page.url:
                    item_page.bring_to_front()
                    return item_page
        else:
            log.info("未找到相应title或url的标签页")
        return self.page.context.pages[0]

    def find(self, ele_type: str, text: str, **kwargs):
        """内置定位器"""
        locator_mapping = {
            "text": "get_by_text",  # 通过文本内容定位
            "alt": "get_by_alt_text",  # 通过替代文本定位元素，通常是图像
            "label": "get_by_label",  # 通过关联标签的文本定位表单控件
            "title": "get_by_title",  # 通过标题属性定位元素
            "tid": "get_by_test_id",  # 根据data-testid属性定位元素（可以配置其他属性）
            "role": "get_by_role",  # 通过显式和隐式可访问性属性进行定位
            "ph": "get_by_placeholder",  # 按占位符定位输入
        }

        locator = locator_mapping.get(ele_type)
        if locator:
            locator_function = getattr(self.page, locator)
            return locator_function(text, **kwargs)
        else:
            log.error(f"定位器类型 {ele_type} 无效")

    def loc_all(self, selector: str):
        """查找所有匹配指定选择器的元素"""
        elements = self.page.locator(selector).all()
        return elements

    @log_action
    def type(self, text: str, selector: str = None):
        """
        模拟逐字符键入文本

        Args:
            text (str): 要输入的文本字符串
            selector (str, optional): 定位页面元素的选择器
        """
        if selector:
            ele = self.locator(selector)
            if ele.is_editable():
                self.page.keyboard.type(text)
        else:
            self.page.keyboard.type(text)

    @log_action
    def press(self, key: str, selector: str = None):
        """
        模拟按键操作（支持同时按下多个键）

        Args:
            key (str): 要按下的键
            selector (str, optional): 定位页面元素的选择器
        """
        if selector:
            ele = self.locator(selector)
            if ele.is_editable():
                self.page.keyboard.press(key)
        else:
            self.page.keyboard.press(key)

    @log_action
    def clear(self, selector: str):
        """清空文本"""
        self.locator(selector).clear()

    @log_action
    def click_all(self, selector: str):
        """对所有匹配的元素列表遍历点击"""
        elements = self.loc_all(selector)
        for ele in elements:
            ele.click()

    def inner_texts(self, selector: str):
        """提取所有匹配的元素的内部文本"""
        elements = self.loc_all(selector)
        text_list = [ele.inner_text() for ele in elements]
        log.info(f"提取选择器匹配的 {selector} 元素的文本: {text_list}")
        return text_list

    @log_action
    def attr_values(self, selector: str, attribute: str):
        """提取所有匹配的元素的指定属性值"""
        elements = self.loc_all(selector)
        attribute_values = [ele.get_attribute(attribute) for ele in elements]
        log.info(f"提取选择器匹配的 {selector} 元素的 {attribute} 属性值: {attribute_values}")
        return attribute_values

    @log_action
    def fill_all(self, selector: str, value: str):
        """在所有匹配的元素列表遍历输入"""
        elements = self.loc_all(selector)
        for element in elements:
            element.fill(value)

    @log_action
    def check(self, selector: str, checked: bool = True):
        """选中或取消选中单选框/复选框"""
        self.locator(selector).set_checked(checked=checked)

    def click_option(self, selector: str, dropdown_selector: str, target_option_text=None, select_all=False):
        """
        在下拉框中点击选择指定的单个/多个选项或全部选项 (适用于动态加载的元素)

        Args：
            selector (str): 下拉框的选择器
            dropdown_selector (str): 选项元素
            target_option_text (str or list, optional): 希望在下拉选项中选择的特定文本，可以是字符串或字符串列表，默认为None
            select_all (bool, optional): 是否选择所有选项，默认为False
        """
        target_option_texts = []

        if not select_all and target_option_text is None:
            log.error("未提供目标选项文本并且未选择全选模式")
            return
        if select_all and target_option_text is not None:
            log.warning("同时选择了全选模式和特定选项文本，将会忽略特定选项文本")
        if target_option_text is not None:
            if isinstance(target_option_text, str):
                target_option_texts = [target_option_text]
            elif isinstance(target_option_text, list):
                target_option_texts = target_option_text
            else:
                log.error("'target_option_text'应为字符串或字符串列表")
                return

        dropdown_btn = self.page.locator(selector)
        dropdown_btn.click()

        if select_all:
            options = self.page.locator(dropdown_selector)
            options_text = options.all_text_contents()
            for option in options_text:
                self.page.locator(f"{dropdown_selector} >> text='{option}'").click()
                log.info(f"已点击选中'{option}'")
        else:
            for text in target_option_texts:
                while True:
                    option = self.page.locator(dropdown_selector)
                    if text in option.all_text_contents():
                        self.page.locator(f"{dropdown_selector} >> text='{text}'").click()
                        log.info(f"已点击选中'{text}'")
                        break
                    else:
                        option.nth(-1).hover()
                        log.info(f"在下拉选项中找不到'{text}' >>> 已悬停至最后一个选项'{option.nth(-1).text_content()}'")

    def select_option(self, selector, option_type="text", option=None):
        """
        在下拉框中选择选项

        Args：
            selector (str): 下拉框的选择器
            option_type (str, 可选): 选项类型。 默认为"text"，可选值为 "text", "index", "value"
            option (str or int, 可选): 要选择的选项。 可以是文本（str），索引（int），值（str），列表（List）
        """
        dropdown = self.page.locator(selector)
        if option_type == "text":
            dropdown.select_option(label=option)
        elif option_type == "index":
            dropdown.select_option(index=option)
        elif option_type == "value":
            dropdown.select_option(value=option)
        else:
            log.warning("无效的选项类型")

    def get_all_options(self, selector, option_type="text"):
        """
        获取下拉框中所有选项的文本或值

        Args：
            selector (str): 下拉框的选择器
            option_type (str, 可选): 选项类型。 默认为 "text"，可选值为 "text", "value"

        Returns (list)：
            包含所有选项文本或值的列表
        """
        dropdown = self.page.locator(selector)
        options = []
        for option in dropdown.locator("option").all():
            if option_type == "text":
                options.append(option.inner_text())
            elif option_type == "value":
                options.append(option.get_attribute("value"))
        return options

    def select_all_options(self, selector, option_type="text"):
        """
        遍历选择下拉框中的所有选项

        Args：
            selector (str): 下拉框的选择器
            option_type (str, 可选): 选项类型。默认为 "text"，可选值为 "text", "value"
        """
        all_options = self.get_all_options(selector, option_type)
        for option in all_options:
            self.select_option(selector, option, option_type)

    @log_action
    def drag_element(self, source: str, target: str):
        """拖动一个元素从源位置到目标位置"""
        self.locator(source).drag_to(self.locator(target))

    @log_action
    def drag_and_drop(self, source, target):
        """执行拖动和释放操作: 将一个元素从源位置拖动到目标位置"""
        self.locator(source).hover()
        self.page.mouse.down()
        self.locator(target).hover()
        self.page.mouse.up()

    def hover(self, selector: str):
        """鼠标悬停至指定元素(也会自动去页面上找到元素，使其出现在可视窗口)"""
        ele = self.locator(selector)
        ele.hover()
        return ele

    @log_action
    def left_click(self, selector: str):
        """悬浮在指定元素后左键点击"""
        self.hover(selector).click()

    @log_action
    def right_click(self, selector: str):
        """悬浮在指定元素后右键点击"""
        self.hover(selector).click(button='right')

    @log_action
    def dbl_click(self, selector: str):
        """悬浮在指定元素后左键双击"""
        self.hover(selector).dblclick()

    @log_action
    def scroll_to_element(self, selector: str):
        """滚动到指定的元素"""
        self.page.evaluate(f"document.querySelector('{selector}').scrollIntoView();")

    @log_action
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.page.evaluate('window.scrollTo(0, 0);')

    @log_action
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.page.evaluate('window.scrollTo(0, document.body.scrollHeight);')

    @log_action
    def execute_js(self, script: str):
        """执行JavaScript脚本"""
        self.page.evaluate(script)

    @log_action
    def upload_file(self, file_path='input[type=file]'):
        """上传文件"""
        ele = self.locator(file_path)
        ele.set_input_files(file_path)

    def save_storage_state(self, path: str):
        """
        保存当前上下文的存储状态到文件

        Args:
            path (str): 存储状态文件的路径和名称
        """
        self.page.context.storage_state(path=path)  # path="state.json"

    def create_context_with_storage(self, path: str):
        """
        创建一个新的上下文，并从指定的存储状态文件中恢复状态

        Args:
            path (str): 存储状态文件的路径和名称

        Returns:
            BrowserContext: 新创建的上下文对象
        """
        return self.page.context.browser.new_context(storage_state=path)

    @log_action
    def inner_text(self, selector: str):
        """获取内部文本"""
        inner_text = self.page.locator(selector).inner_text()
        return inner_text

    @log_action
    def text_content(self, selector: str):
        """获取文本内容"""
        text_content = self.page.locator(selector).text_content()
        return text_content

    @log_action
    def get_attr(self, selector: str, name: str):
        """获取元素的属性值"""
        get_attribute = self.page.locator(selector).get_attribute(name)
        return get_attribute

    @log_action
    def wait_ele_visible(self, locator: str, index: int = None):
        """等待元素出现"""
        if index is None:
            self.page.locator(locator).wait_for(timeout=self.timeout)
        else:
            self.page.locator(locator).nth(index).wait_for(timeout=self.timeout)

    @log_action
    def wait_ele_hidden(self, locator: str, index: int = None):
        """等待元素消失"""
        if index is None:
            self.page.locator(locator).wait_for(timeout=self.timeout, state='hidden')
        else:
            self.page.locator(locator).nth(index).wait_for(timeout=self.timeout, state='hidden')


    @log_action
    def fill_all_from_index(self, selector: str, input_values: list, start_index: int = 1) -> None:
        """模型设计业务：在指定元素列表的索引处遍历输入文本"""
        elements = self.page.locator(selector).all()

        for index, ele in enumerate(elements, start=0):
            if index >= start_index:
                input_index = index - start_index
                if input_index < len(input_values):
                    item = input_values[input_index]
                    ele.fill(item)

    @log_action
    def select_field_options(self, field_types: str, field_type_items: str, start_index: int, hover_field: str = None):
        """模型设计业务：遍历选择字段类型和下拉列表项"""
        elements = self.page.locator(field_types).all()

        for index, ele in enumerate(elements, start=0):
            if index > start_index:
                ele.click()
                if hover_field:
                    self.page.locator(hover_field).hover()
                items = self.page.locator(field_type_items).all()
                item_index = index - start_index
                if item_index < len(items):
                    items[item_index].click()

    def assert_ele_visible(self, selector: str):
        """断言：元素是否可见"""
        ele = self.page.locator(selector)
        is_visible = ele.is_visible(timeout=self.timeout)
        log.info(f"[断言] >>> 元素{selector}是否可见：{is_visible}")
        return is_visible

    def assert_ele_hidden(self, selector: str):
        """断言：元素是否隐藏"""
        ele = self.page.locator(selector)
        is_hidden = ele.is_hidden(timeout=self.timeout)
        log.info(f"[断言] >>> 元素{selector}是否隐藏：{is_hidden}")
        return is_hidden

    def assert_ele_enabled(self, selector: str):
        """断言：元素是否启用（未被禁用）"""
        ele = self.page.locator(selector)
        is_enabled = ele.is_enabled()
        log.info(f"[断言] >>> 元素{selector}是否可用：{is_enabled}")
        return is_enabled

    def assert_ele_disabled(self, selector: str):
        """断言：元素是否被禁用"""
        ele = self.page.locator(selector)
        is_disabled = ele.is_disabled()
        log.info(f"[断言] >>> 元素{selector}是否被禁用：{is_disabled}")
        return is_disabled

    def assert_ele_checked(self, selector: str):
        """断言：单选框/多选框元素是否被选中"""
        ele = self.page.locator(selector)
        if ele.is_checked(timeout=self.timeout):
            log.info(f"[断言] >>> 元素{selector}已被选中")
            return True
        else:
            log.info(f"[断言] >>> 元素{selector}未选中")
            return False

    @log_action
    @assert_result
    def assert_ele_text(self, selector: str, expected_text: str):
        """断言：元素的文本内容是否与预期文本内容匹配"""
        ele_text = self.page.locator(selector).inner_text()
        return ele_text == expected_text

    @log_action
    @assert_result
    def assert_ele_contains_text(self, selector: str, expected_text: str):
        """断言：元素的文本内容是否包含预期文本内容"""
        ele_text = self.page.locator(selector).inner_text()
        return expected_text in ele_text

    @log_action
    @assert_result
    def assert_ele_attr(self, selector: str, name: str, expected_value: str):
        """断言：元素的属性值是否与预期相等"""
        ele_value = self.page.locator(selector).get_attribute(name)
        return ele_value == expected_value

    @log_action
    @assert_result
    def assert_page_title(self, expected_title: str):
        """断言：页面标题是否与预期匹配"""
        page_title = self.page.title()
        return page_title == expected_title

    @log_action
    @assert_result
    def assert_page_url(self, expected_url: str):
        """断言：页面url是否与预期匹配"""
        url = self.page.url
        return url == expected_url
