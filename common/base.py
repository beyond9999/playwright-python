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
        """暂停脚本执行 (仅在有界面模式启动时才有效)"""
        self.page.pause()

    def screenshot(self, selector: str = None, full_page=False):
        """截取屏幕并将其添加至allure报告中"""
        if selector:
            allure_attach_screenshot(page=self.page, selector=selector)
        elif full_page:
            allure_attach_screenshot(page=self.page, full_page=True)
        else:
            allure_attach_screenshot(page=self.page)

    def locator(self, selector: str, position: str = None, index: int = None, frame_name: str = None,
                frame_id: str = None):
        """
        查找并返回元素

        Args：
            selector (str): 元素选择器
            position (str, optional): 元素位置，可以是 "first" 或 "last"
            index (int, optional): 元素索引
            frame_name (str, optional): frame的name属性
            frame_id (str, optional): frame的id属性
        """
        if frame_name:
            element = self.page.frame(frame_name).locator(selector)
        elif frame_id:
            element = self.page.frame_locator(frame_id).locator(selector)
        else:
            element = self.page.locator(selector)

        if position == "first":
            ele = element.first
        elif position == "last":
            ele = element.last
        elif index is not None:
            ele = element.nth(index)
        else:
            ele = element

        ele.wait_for(timeout=self.timeout)
        ele.highlight()

        return ele

    @log_action
    def click(self, selector: str, position: str = None, index: int = None, frame_name: str = None,
              frame_id: str = None):
        """点击元素"""
        ele = self.locator(selector, position, index, frame_name, frame_id)
        if ele.is_enabled():
            ele.click()

        self.screenshot()

    @log_action
    def fill(self, selector: str, input_value: str, position: str = None, index: int = None, frame_name: str = None,
             frame_id: str = None):
        """输入文本"""
        ele = self.locator(selector, position, index, frame_name, frame_id)
        if ele.is_editable():
            ele.clear()
            ele.fill(input_value)

        self.screenshot()

    def mouse_wheel(self, delta_x: float, delta_y: float):
        """
        模拟鼠标滚轮操作

        Args：
            delta_x (float): 横向移动距离，正数表示向右，负数表示向左
            delta_y (float): 纵向移动距离，正数表示向下，负数表示向上
        """
        self.page.mouse.wheel(delta_x, delta_y)

    def wait(self, seconds: float):
        """强制等待"""
        self.page.wait_for_timeout(seconds * 1000)
        log.info(f">>> 等待{seconds}秒")

    def wait_page(self, state: str = "load"):
        """
        等待页面加载到特定状态

        Args：
            state (str, optional): 页面加载状态 (可填 "load"、"network"、"dom", 默认为 "load")
        """
        load_state_mapping = {
            "load": "load",  # 等待页面完全加载
            "network": "networkidle",  # 等待网络空闲
            "dom": "domcontentloaded"  # 等待 DOMContentLoaded 事件触发，即HTML文档被完全加载和解析，不包括样式表、图片和其他资源
        }
        page_state = load_state_mapping.get(state)
        self.page.wait_for_load_state(state=page_state, timeout=self.load_state_timeout)
        log.info(">>> 页面已加载完成")

    def wait_navigation(self):
        """设置页面的默认导航超时时间"""
        self.page.set_default_navigation_timeout(timeout=self.default_navigation_timeout)

    def page_operation(self, reload=False, forward=False, back=False):
        """
        浏览器页面操作

        Args：
            reload: 刷新
            forward: 前进
            back: 回退
        """
        if reload:
            self.page.reload()
        if back:
            self.page.go_back()
        if forward:
            self.page.go_forward()

    def wait_for_url(self, url: str):
        """在页面上设置一个等待，等待URL变为指定的URL"""
        self.page.wait_for_url(url)

    def page_content(self):
        """获取页面的完整HTML内容 (包括文档类型)"""
        html = self.page.content()
        log.info(f"页面的完整HTML内容: {html}")

    def inner_html(self, selector: str):
        """获取某个元素的HTML内容"""
        ele_html = self.locator(selector).inner_html()
        log.info(f"元素的的HTML内容: {ele_html}")

    def get_frames(self):
        """获取页面所有的iframes"""
        frames = self.page.frames
        for f in frames:
            log.info(f"获取到的frames：{f}")

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
            log.warning(f"窗口索引 {page_index} 超出范围")

    @log_action
    def switch_page(self, title=None, url=None):
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
            log.error("未找到相应title或url的标签页")
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
            log.warning(f"无效的定位器类型: {ele_type}")

    @log_action
    def type(self, text: str, selector: str = None):
        """
        模拟人工逐字符键入文本

        Args：
            text (str): 要输入的文本字符串
            selector (str, optional): 定位页面元素的选择器
        """
        if selector:
            ele = self.locator(selector)
            if ele.is_editable():
                ele.focus()
                self.page.keyboard.type(text)
        else:
            self.page.keyboard.type(text)

    @log_action
    def press(self, key: str, selector: str = None):
        """
        模拟按键操作 (支持同时按下多个键)

        Args：
            key (str): 要按下的键 (组合键示例"Control+A")
            selector (str, optional): 定位页面元素的选择器

            以下是一些常见的键盘按键：
                所有字母和数字键 ('a', 'b', 'c', ..., 'z', 'A', 'B', ..., 'Z', '0', '1', ..., '9')
                功能键 ('F1', 'F2', ..., 'F12')
                方向键 ('ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight')
                特殊键 ('Tab', 'Enter', 'Backspace', 'Delete', 'Escape', 'Shift', 'Control', 'Alt', 'Meta',
                      'CapsLock', 'PageUp', 'PageDown', 'End', 'Home', 'Insert', 'ContextMenu')
                符号键 ('!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '`', '~', '[', ']',
                      '{', '}', '|', ';', ':', "'", '"', ',', '<', '.', '>', '/', '?', '\', '|')
        """
        if selector:
            ele = self.locator(selector)
            if ele.is_editable():
                ele.focus()
                self.page.keyboard.press(key)
        else:
            self.page.keyboard.press(key)

    @log_action
    def clear(self, selector: str):
        """清空文本"""
        self.locator(selector).clear()

    @log_action
    def click_elements(self, selector: str):
        """对元素列表遍历点击"""
        elements = self.page.locator(selector).all()
        [ele.click() for ele in elements]

    @log_action
    def fill_elements(self, selector: str, input_value: str):
        """在元素列表遍历输入"""
        elements = self.page.locator(selector).all()
        [ele.fill(input_value) for ele in elements]

    def all_inner_texts(self, selector: str):
        """提取元素列表的内部文本"""
        text_list = self.page.locator(selector).all_inner_texts()
        log.info(f"元素列表 [{selector}] 的文本为: {text_list}")
        return text_list

    def all_attribute_values(self, selector: str, attr: str):
        """提取元素列表的指定属性值"""
        elements = self.page.locator(selector).all()
        attribute_values = [element.get_attribute(attr) for element in elements]
        log.info(f"元素列表 [{selector}] 的属性 {attr} 值为: {attribute_values}")
        return attribute_values

    @log_action
    def set_checked(self, selector: str, checked: bool = True):
        """
        设置单选框 (radio) 和复选框 (checkbox) 的选中状态

        Args：
            selector (str): 定位页面元素的选择器
            checked (bool): 设置选中状态，默认为True
        """
        self.locator(selector).set_checked(checked=checked)

    @log_action
    def all_checkbox_check(self, selector: str, checked: bool = True):
        """复选框 (checkbox) 全选或取消全选"""
        items = self.page.locator(selector).all()
        for item in items:
            item.set_checked(checked=checked)

    @log_action
    def select_option(self, selector, option_type="label", option=None):
        """
        在下拉框中选择选项

        Args：
            selector (str): 下拉框的选择器
            option_type (str, optional): 选项类型。 默认为"text"，可选值为 "text", "index", "value"
            option (str or int, optional): 要选择的选项。 可以是文本（str）、索引（int）、值（str）、列表（List）
        """
        dropdown = self.page.locator(selector)
        if option_type == "label":
            dropdown.select_option(label=option)
        elif option_type == "index":
            dropdown.select_option(index=option)
        elif option_type == "value":
            dropdown.select_option(value=option)
        else:
            log.warning("无效的选项类型")

    def select_all_options(self, selector):
        """
        在下拉框中选择所有选项

        Args:
            selector (str): 下拉框的选择器
        """
        dropdown = self.page.locator(selector)
        # 打开下拉框
        dropdown.click()
        options = dropdown.locator('option').all_inner_texts()
        dropdown.select_option(label=options)

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

    @log_action
    def drag_to(self, source: str, target: str):
        """拖动一个元素从源位置到目标位置"""
        self.locator(source).drag_to(self.locator(target))

    def hover(self, selector: str):
        """鼠标悬停至指定元素(也会自动去页面上找到元素，使其出现在可视窗口)"""
        ele = self.locator(selector)
        ele.hover()
        return ele

    @log_action
    def drag_and_drop(self, source, target):
        """执行拖动和释放操作: 将一个元素从源位置拖动到目标位置"""
        self.hover(source)
        self.page.mouse.down()
        self.hover(target)
        self.page.mouse.up()

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
    def scroll_to_ele(self, selector):
        """滚动到元素出现位置（元素会出现在屏幕的正中间）"""
        self.locator(selector).scroll_into_view_if_needed()
        self.screenshot(full_page=True)

    @log_action
    def scroll_to_top(self):
        """滚动到页面顶部"""
        self.page.evaluate('window.scrollTo(0, 0);')

    @log_action
    def scroll_to_bottom(self):
        """滚动到页面底部"""
        self.page.evaluate('window.scrollTo(0, document.body.scrollHeight);')

    @log_action
    def execute_script(self, script: str, selector: str = None):
        """执行JavaScript脚本"""
        if selector is not None:
            self.locator(selector).evaluate(script)
        else:
            self.page.evaluate(script)

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
        """[模型设计业务]：在指定元素列表的索引处遍历输入文本"""
        elements = self.page.locator(selector).all()

        for index, ele in enumerate(elements, start=0):
            if index >= start_index:
                input_index = index - start_index
                if input_index < len(input_values):
                    item = input_values[input_index]
                    ele.fill(item)

    @log_action
    def select_field_options(self, field_types: str, field_type_items: str, start_index: int, hover_field: str = None):
        """[模型设计业务]：遍历选择字段类型和下拉列表项"""
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
