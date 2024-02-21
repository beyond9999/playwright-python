import os
import yaml


class YamlUtil:
    def __init__(self, *path_parts):
        """
        初始化YamlUtil类，使用一个路径部分列表来构建YAML文件路径
        :param path_parts: 用于构建YAML文件路径的路径部分列表
        """
        self.yaml_file = os.path.join(*path_parts)

    def read_yaml(self):
        """
        读取YAML文件并将其转换为字典
        :return: 来自YAML文件的字典数据
        """
        with open(self.yaml_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
