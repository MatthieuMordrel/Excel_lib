import logging
from pathlib import Path
import json

def setup_logger(log_file: Path = Path("Logs/Current Logs/excel_processor.log")) -> logging.Logger:
    """
    Sets up and configures the logger, clearing the log file before each run.
    Only shows WARNING level and above in console, while maintaining DEBUG level for file logging.
    """
    # Clear the log file before setting up the logger
    with open(log_file, 'w') as f:
        f.write('')  # This will clear the file content

    logger = logging.getLogger("excel_processor")
    logger.setLevel(logging.DEBUG)  # Set base logger level to DEBUG to capture all messages
    
    # Create file handler for all levels
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Log all levels to file
    
    # Create console handler for WARNING and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show WARNING and above in console
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Remove any existing handlers to prevent duplicate logging
    logger.handlers = [file_handler, console_handler]
    
    return logger

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
        
        # Log summary to console with WARNING level to ensure visibility
        logger.warning("\n=== Processing Summary ===")
        logger.warning(f"Total: {total_requests} | Success: {successful_requests} | Failed: {failed_requests}")
        
        if max_depth_reached > 0:
            logger.warning(f"Maximum recursion depth reached: {max_depth_reached} requests")
            
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}") 