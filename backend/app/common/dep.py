from fastapi import Request


async def get_uid(request: Request) -> int:
    """
    从request头部中获取uid信息
    """
    return request.state.uid
