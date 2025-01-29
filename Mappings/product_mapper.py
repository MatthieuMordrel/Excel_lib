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