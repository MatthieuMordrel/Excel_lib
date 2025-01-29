import logging
from typing import Dict, Any
from pathlib import Path
import json

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

def log_request_completion(logger: logging.Logger, result: Dict[str, Any]) -> None:
    """
    Logs the completion of a request.
    
    Args:
        logger: Logger instance
        result: Result dictionary to log
    """
    status = "SUCCESS" if 'error' not in result else "FAILED"
    message = f"Completed {result['file']} {result['sheet']}!{result['cell']} - {status}"
    
    if 'error' in result:
        message += f" - Error: {result['error']}"
    
    logger.info(message)

def log_summary(logger: logging.Logger, log_path: Path) -> None:
    """
    Logs a summary of the processing results.
    
    Args:
        logger: Logger instance
        log_path: Path to the log JSON file
    """
    try:
        with open(log_path, 'r') as f:
            results = json.load(f)
            
        total_requests = len(results)
        successful_requests = len([r for r in results if 'error' not in r])
        failed_requests = total_requests - successful_requests
        
        # Check for recursion depth issues
        max_depth_reached = sum(1 for r in results if 'error' in r and 'Maximum recursion depth reached' in r['error'])
        
        logger.info("\n=== Processing Summary ===")
        logger.info(f"Total requests processed: {total_requests}")
        logger.info(f"Successful requests: {successful_requests}")
        logger.info(f"Failed requests: {failed_requests}")
        
        if max_depth_reached > 0:
            logger.warning(f"Maximum recursion depth reached for {max_depth_reached} requests")
            
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}") 