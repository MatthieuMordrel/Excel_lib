from typing import List, Dict, Any
import json
from pathlib import Path

def has_multiplication_or_division(result: Dict[str, Any]) -> bool:
    """Check if result or any nested reference has multiplication/division"""
    # Check current object
    if result.get('isMultiplication') or result.get('isDivision'):
        return True
    
    # Recursively check all references
    for ref in result.get('references', []):
        if has_multiplication_or_division(ref):
            return True
    
    return False

def has_no_formula(result: Dict[str, Any]) -> bool:
    """Check if result or any nested reference indicates no formula in file"""
    if result.get('formula') == "Cell has no formula in file":
        return True
    for ref in result.get('references', []):
        if has_no_formula(ref):
            return True
    return False

def clean_result(result: Dict[str, Any], is_root: bool = True) -> Dict[str, Any]:
    """Clean result and its references to only keep required properties.
    Only show references for root object or until we find a key component."""
    
    # Base case: if we find a key component, return it without references
    if not is_root and (result.get('isElement') or result.get('isProduct') or result.get('isBaseMaterial')):
        return {
            'productID': result.get('productID'),
            'isElement': result.get('isElement'),
            'isProduct': result.get('isProduct'),
            'isBaseMaterial': result.get('isBaseMaterial'),
            'value': result.get('value'),
            'sheet': result.get('sheet'),
            'cell': result.get('cell'),
            'references': []  # No need to show references for key components
        }
    
    # For root or intermediate objects, process references
    cleaned = {
        'productID': result.get('productID'),
        'isElement': result.get('isElement'),
        'isProduct': result.get('isProduct'),
        'isBaseMaterial': result.get('isBaseMaterial'),
        'value': result.get('value'),
        'sheet': result.get('sheet'),
        'cell': result.get('cell'),
        'references': [
            clean_result(ref, is_root=False)  # Process references as non-root
            for ref in result.get('references', [])
        ] if is_root else []  # Only show references for root object
    }
    
    return cleaned

def process_logs(input_path: Path, output_path: Path) -> None:
    """Process log file according to requirements"""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'r') as f:
        data: List[Dict[str, Any]] = json.load(f)
    
    # First filter, then clean
    filtered_data = [
        result 
        for result in data 
        if not has_multiplication_or_division(result) 
        and not has_no_formula(result)
    ]
    
    processed_data = [clean_result(result) for result in filtered_data]
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(processed_data, f, indent=2)

if __name__ == "__main__":
    # Use absolute path to avoid relative path issues
    input_path = Path(__file__).parent.parent / "Logs" / "log.json"
    output_path = Path(__file__).parent.parent /  "post_processing" /"processed_log.json"
    process_logs(input_path, output_path) 