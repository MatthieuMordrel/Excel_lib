import json
from pathlib import Path
from typing import Dict, Any, List

def has_errors(entry: Dict[str, Any]) -> bool:
    """Check if entry or any of its references have errors"""
    if entry.get('error'):
        return True
    
    # Check nested references
    for ref in entry.get('references', []):
        if has_errors(ref):
            return True
    
    return False

def is_drawer_formula(formula: str) -> tuple[bool, str]:
    """
    Check if formula matches drawer patterns and return type
    Returns (is_drawer, drawer_type)
    """
    if not formula:
        return (False, "")
    
    # Clean and split formula
    parts = formula.strip("=+").split("+")
    
    # Check if we have exactly 3 parts
    if len(parts) != 3:
        return (False, "")
    
    # Check if parts follow pattern W36+W35+W34 or R36+R35+R34
    parts = [p.strip() for p in parts]
    
    # Check for W pattern
    if all(p.startswith('W') for p in parts) and parts == [f'W{i}' for i in range(36, 33, -1)]:
        return (True, "binnenpottenlade")
    
    # Check for R pattern  
    if all(p.startswith('R') for p in parts) and parts == [f'R{i}' for i in range(36, 33, -1)]:
        return (True, "binnenlade")
        
    return (False, "")

def get_drawer_size(references: List[Dict[str, Any]], formula_type: str) -> float:
    """Extract drawer size from references recursively"""
    size_cell = 'V36' if formula_type == 'binnenpottenlade' else 'Q36'
    
    def search_refs(refs: List[Dict[str, Any]]) -> float:
        for ref in refs:
            if ref.get('cell') == size_cell:
                return float(ref.get('value', 0.0))
            # Recursively search nested references
            if ref.get('references'):
                size = search_refs(ref['references'])
                if size > 0:
                    return size
        return 0.0
    
    return search_refs(references)

def process_entry(entry: Dict[str, Any], is_top: bool = True) -> Dict[str, Any]:
    """Process individual log entry to extract required properties"""
    # Check for drawer formula pattern
    is_drawer, drawer_type = is_drawer_formula(entry.get('cleaned_formula', ''))
    
    if is_drawer:
        return {
            "type": drawer_type,
            "size": get_drawer_size(entry.get('references', []), drawer_type),
            "value": entry.get('value', 0)
        }
    
    # Determine entry type first
    entry_type = "product" if entry.get("isProduct", False) else "element" if entry.get("isElement", False) else "baseMaterial" if entry.get("isBaseMaterial", False) else "none"
    
    # For elements, return only type and id
    if entry_type == "element":
        return {
            "type": entry_type,
            "id": f"{entry.get('sheet')}_{round(entry.get('value', 0), 3)}"
        }
    if entry_type == "baseMaterial":
        return {
            "type": entry_type,
            "id": entry.get("cell")
        }
    if entry_type == "product" and not is_top:
        return {
            "type": entry_type,
            "id": entry.get("productID")
        }
    
    # Create initial dictionary for non-element entries
    processed_entry = {
        "type": entry_type,
        "file": entry.get("file"),
        "sheet": entry.get("sheet"),
        "cell": entry.get("cell"),
        "cleaned_formula": entry.get("cleaned_formula"),
        "value": entry.get("value") if entry.get("cleaned_formula") == "Cellhasnoformulainfile" else None,
        "id": entry.get("productID") if entry.get("isProduct", False) else entry.get("cell") if entry.get("isBaseMaterial",False) else None,
        "references": [process_entry(ref, False) for ref in entry.get("references", [])] if entry.get("references") and (not entry.get("isProduct", False) or is_top) else None
    }
    
    # Remove null values
    return {k: v for k, v in processed_entry.items() if v is not None}

def simplify_log(input_path: Path, output_path: Path, error_output_path: Path) -> None:
    """Main processing function that separates entries with and without errors"""
    with open(input_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # Separate entries with and without errors
    valid_entries: List[Dict[str, Any]] = []
    error_entries: List[Dict[str, Any]] = []
    
    for entry in log_data:
        if has_errors(entry):
            error_entries.append(entry)
        else:
            valid_entries.append(process_entry(entry, True))
    
    # Write valid entries to main output file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(valid_entries, f, indent=2)
    
    # Write error entries to error log file
    with open(error_output_path, 'w', encoding='utf-8') as f:
        json.dump(error_entries, f, indent=2)

if __name__ == "__main__":
    input_file = Path("Logs/Current Logs/log.json")
    output_file = Path("Logs/Current Logs/simplified_log.json")
    error_file = Path("Logs/Current Logs/error_log.json")
    
    simplify_log(input_file, output_file, error_file)
    print(f"Simplified log created at: {output_file}")
    print(f"Error log created at: {error_file}")