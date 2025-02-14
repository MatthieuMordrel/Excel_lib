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

def process_entry(entry: Dict[str, Any], is_top: bool = True) -> Dict[str, Any]:
    """Process individual log entry to extract required properties"""
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