"""
Logging utilities for the scanner controller
"""
import logging
import os

def configure_logging(log_file="scanner_controller.log", level=logging.INFO):
    """
    Configure logging for the scanner controller
    
    Parameters:
        log_file: Path to the log file
        level: Logging level (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Add console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    return logging.getLogger('')
