import pytest
from utils.read_yaml import YamlUtil as YU
from pages_action.create_app import AppListAction


yaml_util = YU("./datas/create_app_data.yaml")
create_app_data = yaml_util.read_yaml()["create_app_params"]


@pytest.fixture(scope="class")
def click_create(page):
    AppListAction(page).click_create_app(page)


# 参数化
@pytest.fixture(params=create_app_data)
def create_app_params(request):
    return request.param