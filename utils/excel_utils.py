import json
from typing import Dict

def save_to_log(result: Dict, log_path: str) -> None:
    """
    Saves extraction result to a JSON log file.
    
    Args:
        result (Dict): Dictionary containing extraction results
        log_path (str): Path to the log file
    """
    with open(log_path, 'a') as f:
        json.dump(result, f, indent=2)
        f.write('\n') 