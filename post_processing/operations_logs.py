from typing import List, Dict, Any
import json
from pathlib import Path
import argparse

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

def analyze_operations(log_path: Path, output_path: Path) -> None:
    """Analyzes a log file and generates operation statistics"""
    with open(log_path, 'r') as f:
        results: List[Dict[str, Any]] = json.load(f)

    stats: Dict[str, int] = {
        "total_formulas": 0,
        "has_both": 0,
        "has_multiplication": 0,
        "has_division": 0,
        "has_neither": 0
    }

    def check_references(refs: List[Dict[str, Any]]) -> bool:
        for ref in refs:
            if ref.get('isMultiplication'):
                return True
            if ref.get('isDivision'):
                return True
            if check_references(ref.get('references', [])):
                return True
        return False

    for result in results:
        stats["total_formulas"] += 1
        
        has_mul = result.get('isMultiplication') or check_references(result.get('references', []))
        has_div = result.get('isDivision') or check_references(result.get('references', []))
        
        if has_mul and has_div:
            stats["has_both"] += 1
        elif has_mul:
            stats["has_multiplication"] += 1
        elif has_div:
            stats["has_division"] += 1
        if not has_mul and not has_div:
            stats["has_neither"] += 1

    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Generated operation stats in {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Excel formula log file')
    parser.add_argument('--input', type=Path, required=True, help='Path to log.json file')
    parser.add_argument('--output', type=Path, default=Path("Logs/operation_stats.json"), 
                      help='Output path for statistics')
    args = parser.parse_args()
    
    analyze_operations(args.input, args.output) 