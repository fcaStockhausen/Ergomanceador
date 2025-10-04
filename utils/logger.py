"""Logging configuration"""

import logging


def setup_logger():
    """Setup logging to file"""
    logging.basicConfig(
        filename='game_debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s',
        filemode='w'
    )


# Create logger instance for use throughout the codebase
logger = logging.getLogger(__name__)
