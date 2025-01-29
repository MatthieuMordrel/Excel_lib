from pathlib import Path
import json

class ProductMapper:
    """Handles loading and mapping of product information from JSON."""
    
    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.product_mapping = {}
        self.reverse_mapping = {}  # To store the reverse lookup
        
    def load_mapping(self):
        """
        Loads the product mapping from the JSON file and creates reverse mapping.
        """
        try:
            with open(self.json_path, 'r') as f:
                self.product_mapping = json.load(f)
                # Create reverse mapping for faster lookup
                self.reverse_mapping = {v: k for k, v in self.product_mapping.items()}
        except Exception as e:
            print(f"Error loading product mapping: {str(e)}")
            self.product_mapping = {}
            self.reverse_mapping = {}
    
    def enrich_result(self, result: dict) -> dict:
        """Adds product information to a single result."""
        # Create the lookup key from the result
        lookup_key = f"{result['file']}_{result['sheet']}_{result['cell']}".replace(" ", "")
        
        # Check if this key exists in our reverse mapping
        product_id = self.reverse_mapping.get(lookup_key)
        
        result['isProduct'] = product_id is not None
        result['productID'] = product_id
        
        # If this result has references, enrich them too
        if 'references' in result:
            result['references'] = [self.enrich_result(ref) for ref in result['references']]
        
        return result
    
    def enrich_results(self, results: list) -> list:
        """Adds product information to a list of results."""
        return [self.enrich_result(result) for result in results] 