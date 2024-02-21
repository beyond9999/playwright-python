import time
import allure
import pytest


@allure.feature("登录")
@allure.story("用户登录")
@allure.title("有效用户登录")
@pytest.mark.parametrize("usr, pwd", [("autotest", "ABCabc@123")])
def test_login(p, usr, pwd):
    with allure.step("填写用户名和密码"):
        p.fill("#username", usr)
        p.fill("#password", pwd)
    with allure.step("点击登录按钮"):
        p.click("*[type='submit']")
    with allure.step("断言"):
        p.assert_ele_hidden("*[type='submit']")


@pytest.mark.parametrize("option", ['新模板'])
def test_create_app(p, option):
    p.click("//span[text()='新建应用']")
    p.fill("//fly-form-item[1]//input", f"auto{time.strftime('%Y_%m_%d_%H_%M_%S')}")
    p.fill("//fly-form-item[2]//input", f"auto{time.strftime('%Y%m%d%H%M%S')}")
    p.click("fly-select-item")
    p.click(f".ra-select-item-option-content >> text={option}")
    p.click("//*[contains(text(), '确定')]")


@pytest.mark.parametrize("group_name, group_code", [("group", f"code{time.strftime('%Y_%m_%d_%H_%M_%S')}")])
def test_create_dict_group(p, group_name, group_code):
    p.click("//div[text()='数据字典']")
    p.right_click(".ra-tree-treenode-switcher-open .ra-tree-title")
    p.click("span >> text='新增字典分组'")
    p.fill("//fly-form-item[1]//input", group_name)
    p.fill("//fly-form-item[2]//input", group_code)
    p.click("span >> text='确定'")


@pytest.mark.parametrize("dict_name, dict_code, dict_type", [("string", "string", "字符串"), ("number", "number", "数字")])
def test_create_dict(p, page, dict_name, dict_code, dict_type):
    p.right_click("span >> text='group'")
    p.click("span >> text='新增字典'")
    p.fill("//fly-form-item[1]//input", dict_name)
    p.fill("//fly-form-item[2]//input", dict_code)
    p.click("//form//fly-select")
    p.click(f"//div[text()='{dict_type}']")
    p.click("span >> text='确定'")


@pytest.mark.parametrize("item_name, item_value, parent_dict", [("字符串", "string", "string"), ("数字", "666", "number")])
def test_create_dict_item(p, item_name, item_value, parent_dict):
    p.click(f"span >> text='{parent_dict}'")
    p.click(f"span >> text='新增字典项'")
    p.fill("//fly-form-item[1]//input", item_name)
    p.fill("//fly-form-item[2]//input", item_value)
    p.click("span >> text='确定'")


def test_create_module(p):
    p.click("//div[text()='模块管理']")
    p.click("span >> text='新建模块'")
    p.click("div.template-title__name >> text='后端模板'")
    input_value = f"ser{time.strftime('%Y%m%d%H%M%S')}"
    p.fill("//fly-form-item[1]//input", input_value)
    p.fill("//fly-form-item[2]//input", input_value)
    p.click("span >> text='确定'")


@pytest.mark.parametrize("model_name", ["订单"])
def test_create_model(p, setup_switch_tab, model_name):
    p.left_click("//fly-tools-tabs//*[contains(text(), '模型')]")
    p.hover("button.ra-btn.ra-dropdown-trigger > i")
    p.left_click("//li[contains(text(), '新建模型')]")
    p.fill("//fly-modal-container//fly-form-item[1]//input", model_name)
    p.fill("//fly-modal-container//fly-form-item[2]//input", f"Table{time.strftime('%Y%m%d%H%M%S')}")
    p.fill("//fly-modal-container//fly-form-item[3]//input", f"table{time.strftime('%Y_%m_%d_%H_%M_%S')}")
    p.click("span >> text='确认'")


def test_edit_table_field(p, page, setup_close_tab, teardown_open_attr):
    p.dbl_click(".ra-tree-title >> text='订单'")
    p.click(".ra-btn-primary >> text='添加字段'")
    p.click("//td[5]//fly-select-item[contains(text(), '文本')]")
    p.hover(".ra-select-item-option-content >> text='序列号'")

    items_loc = '.ra-select-item-option-content'
    items_text = p.inner_texts(items_loc)
    [p.click(".ra-btn-primary >> text='添加字段'") for _ in range(len(items_text) - 1)]
    p.select_field_options(hover_field=".ra-select-item-option-content >> text='序列号'",
                           field_types="//td[5]//fly-select-item",
                           field_type_items=items_loc,
                           start_index=8)
    p.fill_all_from_index("//td[4]//input", items_text, start_index=8)
    field_code = ['code_varchar', 'code_longtext', 'code_int', 'code_bigint', 'code_decimal', 'code_datetime',
                  'code_bit', 'code_dict_str', 'code_dict_num', 'code_quote', 'code_master_slave', 'code_serial',
                  'code_enumerate', 'emp', 'dept', 'multi_emp', 'multi_dept']
    p.fill_all_from_index("//td[3]//input", field_code, start_index=8)


@pytest.mark.parametrize("index, dict", [("17", "string"), ("18", "number")])
def test_set_dict_field_attr(p, setup_switch_tab, index, dict):
    p.click(f"//tr[{int(index)}]/td[2]")
    p.click("//fly-form-item//fly-tree-select")
    p.click(selector="//fly-tree//fly-tree-node-switcher", index=-1)
    p.click(f"span >> text='{dict}'")


@pytest.mark.parametrize("index, serial", [("19", "fly_{{DATE:yyyyMMddHHmmssSSS}}")])
def test_set_serial_field_attr(p, setup_switch_tab, index, serial):
    p.click(f"//tr[{int(index)}]/td[2]")
    p.click("fly-form-item span >> text='查看'")
    p.fill("fly-form-item:nth-child(1) textarea", serial)
    p.click("button > span >> text='生成'")
    p.click("span >> text='确认'")


@pytest.mark.parametrize("enum_name, enum_code, enum_type", [("enum_name", "enum_code", "字符串")])
def test_set_enum_field_attr(p, setup_switch_tab, enum_name, enum_code, enum_type):
    p.click("//tr[20]/td[2]")
    p.click("fly-form-item span >> text='配置'")
    p.fill("//fly-modal-container//div[2]//fly-form-item[1]//input", enum_name)
    p.fill("//fly-modal-container//div[2]//fly-form-item[2]//input", enum_code)
    p.click("//fly-modal-container//fly-select")
    p.click(f"//fly-option-item/div[text()='{enum_type}']")

    p.click("span >> text='新增一行'")
    p.fill("//div/fly-form-item[1]//div/input", enum_name)
    p.fill("//div/fly-form-item[2]//div/input", enum_code)
    p.click("span >> text='确定'")


def test_set_model_attr(p, setup_switch_tab):
    p.click(selector="//div[text()='模型字段配置']", position="last")
    p.click("//fly-form-item[7]//button")
    p.click("//fly-form-item[8]//button")
    p.click("//fly-form-item[10]//button")

    p.click("span >> text='保存全部'")
    p.wait_ele_visible("span >> text='保存成功'")