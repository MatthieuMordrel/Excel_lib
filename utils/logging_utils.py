import logging
from typing import Dict, Any
from pathlib import Path

def setup_logger(log_file: Path = Path("excel_processor.log")) -> logging.Logger:
    """
    Sets up and configures the logger.
    
    Args:
        log_file: Path to the log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("excel_processor")
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_result(logger: logging.Logger, result: Dict[str, Any]) -> None:
    """
    Logs the result of a cell extraction.
    
    Args:
        logger: Logger instance
        result: Result dictionary to log
    """
    if 'error' in result:
        logger.error(f"Error processing {result['file']} {result['sheet']}!{result['cell']}: {result['error']}")
    else:
        logger.info(f"Processed {result['file']} {result['sheet']}!{result['cell']}")
        if 'resolvedReferences' in result:
            logger.debug(f"Resolved references: {len(result['resolvedReferences'])}") 