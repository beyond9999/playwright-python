import os
import time
import logging
from pathlib import Path

# log_format = '%(levelname)s\t%(asctime)s\t[%(filename)s:%(lineno)d]\t%(message)s'
log_format = '%(levelname)s\t%(asctime)s.%(msecs)03d\t%(message)s'

now_time = time.strftime('%Y-%m-%d-%H_%M_%S')
timestamp = str(time.time()).replace('.', '')[-3:]
log_file_path = Path('outputs/logs') / f"{now_time}_{timestamp}.log"


def get_logger(log_file_path, log_level=logging.INFO, log_format=log_format):
    log_dir = log_file_path.parent
    os.makedirs(log_dir, exist_ok=True)

    # 创建logger对象
    logger = logging.getLogger()
    if not logger.handlers:
        # 设置日志级别
        logger.setLevel(log_level)
        # 添加控制器
        sh = logging.StreamHandler()
        fh = logging.FileHandler(log_file_path, encoding='utf-8')
        # 向log文件输出的日志级别
        fh.setLevel(log_level)
        # 设置日志格式
        formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        # 将日志格式添加到控制器
        sh.setFormatter(formatter)
        fh.setFormatter(formatter)
        # 将控制器添加到日志器
        logger.addHandler(sh)
        logger.addHandler(fh)
    return logger


log = get_logger(log_file_path)
