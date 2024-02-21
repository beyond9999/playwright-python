import time
import allure
import pytest


@allure.feature("登录")
@allure.story("用户登录")
@allure.title("有效用户登录")
@pytest.mark.parametrize("usr, pwd", [("autotest", "ABCabc@123")])
def test_login(p, usr, pwd, page):
    with allure.step("填写用户名&密码"):
        p.fill("input[type='text']", usr)
        p.fill("input[type='password']", pwd)
    with allure.step("点击登录按钮"):
        p.click("#kc-login")
    with allure.step("断言"):
        p.assert_ele_hidden("#kc-login")


@pytest.mark.parametrize("option", ["旧模板"])
def test_create_app(p, option):
    p.click(".add-app-btn")
    p.fill("input[formcontrolname='name']", f"auto{time.strftime('%Y%m%d%H%M%S')}")
    # p.fill("input[formcontrolname='code']", f"auto{time.strftime('%Y%m%d%H%M%S')}")
    p.click("fly-select[formcontrolname='templateVersionType']")
    p.click(f"fly-option-item[title='{option}']")
    p.click("span >> text='确定'")


@pytest.mark.parametrize("group_name, group_code", [("group", f"code{time.strftime('%Y_%m_%d_%H_%M_%S')}")])
def test_create_dict_group(p, group_name, group_code):
    p.click("//div[text()='数据字典']")
    p.right_click(".ra-tree-treenode-switcher-open .ra-tree-title")
    p.click("span >> text='新增字典分组'")
    p.fill("input[formcontrolname='name']", group_name)
    p.fill("input[formcontrolname='code']", group_code)
    p.click("span >> text='确定'")


@pytest.mark.parametrize("dict_name, dict_code, dict_type", [("string", "string", "字符串"), ("number", "number", "数字")])
def test_create_dict(p, page, dict_name, dict_code, dict_type):
    p.right_click("span >> text='group'")
    p.click("span >> text='新增字典'")
    p.fill("input[formcontrolname='name']", dict_name)
    p.fill("input[formcontrolname='code']", dict_code)
    p.click("fly-select[formcontrolname='dataType']")
    p.click(f"fly-option-item[title='{dict_type}']")
    p.click("span >> text='确定'")


@pytest.mark.parametrize("item_name, item_value, parent_dict", [("字符串", "string", "string"), ("数字", "666", "number")])
def test_create_dict_item(p, item_name, item_value, parent_dict):
    p.click(f"span >> text='{parent_dict}'")
    p.click(f"span >> text='新增字典项'")
    p.fill("input[formcontrolname='name']", item_name)
    p.fill("input[formcontrolname='code']", item_value)
    p.click("span >> text='确定'")


def test_create_module(p):
    p.click("//div[text()='模块管理']")
    p.click("span >> text='新建模块'")
    p.click("div.template-title__name >> text='后端-默认模板'")
    input_value = f"ser{time.strftime('%Y%m%d%H%M%S')}"
    p.fill("input[formcontrolname='name']", input_value)
    p.fill("input[formcontrolname='code']", input_value)
    p.click("span >> text='确定'")
    p.assert_ele_hidden("span >> text='确定'")


@pytest.mark.parametrize("model_name", ["订单"])
def test_create_model(p, switch_tab, model_name):
    p.left_click("//fly-tools-tabs//*[contains(text(), '模型')]")
    p.hover("button.ra-btn.ra-dropdown-trigger > i")
    p.left_click("//li[contains(text(), '新建模型')]")
    p.fill(".ra-modal input[formcontrolname='displayName']", model_name)
    p.fill(".ra-modal input[formcontrolname='code']", f"Code{time.strftime('%Y%m%d%H%M%S')}")
    p.fill(".ra-modal input[formcontrolname='name']", f"table{time.strftime('%Y_%m_%d_%H_%M_%S')}")
    p.click(".ra-modal button.ra-btn-primary")


def test_edit_table_field(p, page, close_tab, open_attr):
    p.dbl_click(".ra-tree-title >> text='订单'")
    p.click(".ra-btn-primary >> text='添加字段'")
    p.click("//td[5]//fly-select-item[contains(text(), '文本')]")

    items_loc = '.ra-select-item-option-content'
    items_text = p.inner_texts(items_loc)
    [p.click(".ra-btn-primary >> text='添加字段'") for _ in range(len(items_text) - 1)]
    p.select_field_options(
        field_types="//td[5]//fly-select-item",
        field_type_items=items_loc,
        start_index=5
    )
    p.fill_all_from_index("//td[4]//input", items_text, start_index=5)
    field_code = [
        'code_varchar', 'code_longtext', 'code_int', 'code_bigint',
        'code_decimal', 'code_datetime', 'code_bit', 'code_dict_str',
        'code_dict_num', 'code_quote', 'code_master_slave', 'code_serial',
        'code_enumerate'
    ]
    p.fill_all_from_index("//td[3]//input", field_code, start_index=5)


@pytest.mark.parametrize("index, dict", [("14", "string"), ("15", "number")])
def test_set_dict_field_attr(p, switch_tab, index, dict):
    p.click(f"//tr[{int(index)}]/td[2]")
    p.click("//fly-form-item//fly-tree-select")
    p.click(selector="//fly-tree//fly-tree-node-switcher", position="last")
    p.click(f"span >> text='{dict}'")


@pytest.mark.parametrize("index, serial", [("16", "fly_{{DATE:yyyyMMddHHmmssSSS}}")])
def test_set_serial_field_attr(p, switch_tab, index, serial):
    p.click(f"//tr[{int(index)}]/td[2]")
    p.click("fly-form-item span >> text='查看'")
    p.fill("textarea[formcontrolname='sequenceRule']", serial)
    p.click("button > span >> text='生成'")
    p.click("button > span >> text='确认'")


@pytest.mark.parametrize("enum_name, enum_code, enum_type", [("enum_name", "enum_code", "字符串")])
def test_set_enum_field_attr(p, switch_tab, enum_name, enum_code, enum_type):
    p.click("//tr[17]/td[2]")
    p.click("fly-form-item span >> text='配置'")
    p.fill("input[formcontrolname='name']", enum_name)
    p.fill("input[formcontrolname='code']", enum_code)
    p.click(".ra-modal fly-select[formcontrolname='type']")
    p.click(f".ra-select-item-option-content >> text='{enum_type}'")

    p.click("span >> text='新增一行'")
    p.fill("input[formcontrolname='desc']", enum_name)
    p.fill("input[formcontrolname='value']", enum_code)
    p.click(".ra-btn-primary.ng-star-inserted")


def test_set_model_attr(p, switch_tab):
    p.click(selector="//div[text()='模型字段配置']", position="last")
    p.click("//fly-form-item[7]//button")
    p.click("//fly-form-item[8]//button")
    p.click("//fly-form-item[10]//button")
    p.click("//fly-form-item[11]//button")
    p.click("fly-form-item span >> text='索引管理'")
    p.click("button > span.ng-star-inserted >> text='添加项'")
    p.fill(".ra-modal input[formcontrolname='name']", "only")
    p.click(".ra-modal .ra-select-selector")
    p.click(".ra-select-item > div >> text='唯一索引'")

    p.click_option(
        selector="//td[3]//fly-select-search/input",
        dropdown_selector=".ra-select-item-option > div",
        target_option_text="序列号"
    )
    p.click("span >> text='确认'")
    p.click("span >> text='保存全部'")
    p.wait_ele_visible("span >> text='保存成功'")
