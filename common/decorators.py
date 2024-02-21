import time
from functools import wraps
from utils.logger import log


def timer(func):
    """记录函数的执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        log.info(f"函数 {func.__name__} 执行时间：{execution_time:.3f} 秒")
        return result
    return wrapper


def log_action(action):
    """装饰器：记录操作执行和参数"""
    @wraps(action)
    def wrapper(self, *args, **kwargs):
        action_name = action.__name__
        action_message = f"[操作] --> {action_name}"
        if args or kwargs:
            args_str = ', '.join(map(repr, args))
            kwargs_str = ', '.join(f'{k}={v!r}' for k, v in kwargs.items())
            all_args = ', '.join(filter(None, [args_str, kwargs_str]))
            action_message += f" [参数] --> {all_args}"

        try:
            result = action(self, *args, **kwargs)
        except Exception as e:
            log.error(f"执行 {action_name} 时发生异常, 异常信息：{str(e)}")
            raise e

        log.info(action_message)
        return result

    return wrapper


def assert_result(assertion):
    """装饰器：添加断言结果检查"""
    @wraps(assertion)
    def wrapper(self, *args, **kwargs):
        result = assertion(self, *args, **kwargs)
        if not result:
            raise AssertionError(f"[断言失败]：{assertion.__name__}")
        return result

    return wrapper
