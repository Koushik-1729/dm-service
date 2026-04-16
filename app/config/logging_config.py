import logging
import sys
from loguru import logger

from app.config.app_config import app_config


class InterceptHandler(logging.Handler):
    """Intercepts standard logging and routes to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Configure loguru as the application logger."""
    log_level = app_config.log_level

    # Remove default loguru handler
    logger.remove()

    # Add stdout handler with formatting
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Suppress noisy loggers
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"]:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    logger.info(f"Logging configured: level={log_level}, env={app_config.env}")
