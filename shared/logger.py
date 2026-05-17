"""
Logging configuration for CodeOrbit AI
Uses loguru for better logging experience
"""

import sys
from pathlib import Path
from loguru import logger
from .config import settings

# Remove default handler
logger.remove()

# Add console handler with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# Add file handler for errors
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)

# Add file handler for all logs
logger.add(
    log_dir / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG" if settings.debug else "INFO",
    rotation="50 MB",
    retention="14 days",
    compression="zip",
)

# Export logger
__all__ = ["logger"]

# Made with Bob
