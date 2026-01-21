import logging
from loguru import logger


# 参考自：https://gist.github.com/nkhitrov/a3e31cfcc1b19cba8e1b626276148c49


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def init_logging():
    # 获取所有uvicorn的日志设定，并重置
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )

    for uvicorn_logger in loggers:
        # 为了防止日志重复输出
        uvicorn_logger.propagate = False
        uvicorn_logger.handlers = [InterceptHandler()]
