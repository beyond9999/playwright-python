import os
import configparser
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent


class Config(object):
    """
    公共配置类
    """
    _instance = None

    def __init__(self, cfile=None, **ckwargs):
        """
        :param cfile: 配置文件路径
        :param ckwargs: ConfigParser参数
        :return configparser.ConfigParser
        """
        self.config = configparser.ConfigParser(**ckwargs)
        if cfile is None:
            cfile = self.get_default_path()
        if not os.path.exists(cfile):
            raise ValueError(f"文件: {cfile} 不存在")
        self.config.read(cfile)

    @staticmethod
    def get_default_path():
        """
        获取默认配置文件路径
        :return: 配置文件路径
        """
        return base_path / "config.ini"

    # 使用config对象
    def __call__(self):
        return self.config

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


read_cfg = Config(cfile=base_path / "config.ini")
