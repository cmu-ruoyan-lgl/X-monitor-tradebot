import asyncio
import functools

from tw_client import reuse_cookies, get_cookies, change_cookies


def catch_error(func):
    """
    统计函数耗费时间函数
    """
    @functools.wraps(func)
    async def async_warp(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)

    @functools.wraps(func)
    def sync_warp(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
    # 判断函数是否为异步函数
    if asyncio.iscoroutinefunction(func):
        return async_warp
    else:
        return sync_warp