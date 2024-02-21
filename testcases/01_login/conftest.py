import pytest
from utils.read_yaml import YamlUtil as YU

invalid = YU("./datas/invalid_login_data.yaml")
invalid_login_data = invalid.read_yaml()["login_params"]

yaml_util = YU("./datas/login_data.yaml")
login_data = yaml_util.read_yaml()["login_params"]


# @pytest.fixture(scope="session", autouse=True)
# def navigate_to_login(page):
#     yield page

# 使用fixture将数据提供给测试用例
@pytest.fixture(params=invalid_login_data)
def invalid_login_params(request):
    return request.param


@pytest.fixture(params=login_data)
def login_params(request):
    return request.param