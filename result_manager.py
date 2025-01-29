from pathlib import Path
import json
import os

class ResultManager:
    """Handles loading, saving, and managing results."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        
    def load_existing_results(self) -> list:
        """Loads existing results from the log file."""
        if not os.path.exists(self.log_path):
            return []
            
        try:
            with open(self.log_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def save_results(self, results: list):
        """Saves results to the log file, overwriting any existing content."""
        # Reorder each result to have references last
        ordered_results = []
        for result in results:
            ordered_result = {k: v for k, v in result.items() if k != 'references'}
            if 'references' in result:
                ordered_result['references'] = result['references']
            ordered_results.append(ordered_result)
        
        # Save the ordered results
        with open(self.log_path, 'w') as f:
            json.dump(ordered_results, f, indent=2) 