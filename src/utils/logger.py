"""Logging utility module"""
import sys
from loguru import logger
from .config import config_manager


def setup_logger():
    """Setup application logger"""
    config = config_manager.config
    
    # Remove default handler
    logger.remove()
    
    # Add custom handler
    logger.add(
        sys.stdout,
        level=config.logging.level,
        format=config.logging.format,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/flipkart_scraper.log",
        level=config.logging.level,
        format=config.logging.format,
        rotation="10 MB",
        retention="7 days"
    )
    
    return logger

# Initialize logger
app_logger = setup_logger()
