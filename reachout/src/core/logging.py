import sys
import logging
from loguru import logger


def setup_logging():
    logging.getLogger().handlers = []

    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                "level": "INFO",
                "filter": lambda record: record["level"].no < logging.ERROR
            },
            {
                "sink": sys.stderr,
                "format": "<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <RED><level>{level: <8}</level></RED> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <bold><level>{message}</level></bold>",
                "level": "ERROR"
            },
            {
                "sink": "logs/app.log",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                "level": "DEBUG",
                "rotation": "10 MB",
                "retention": "10 days",
                "compression": "zip",
            }
        ]
    )

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False