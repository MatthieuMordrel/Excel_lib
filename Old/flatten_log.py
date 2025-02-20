import json
from pathlib import Path
from typing import Dict, Any, List

def has_multiplication(entry: Dict[str, Any]) -> bool:
    """Check if entry or any of its references contain multiplication"""
    if '*' in entry.get('cleaned_formula', ''):
        return True
    
    for ref in entry.get('references', []):
        if has_multiplication(ref):
            return True
    
    return False

def flatten_references(references: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten nested references into a single list"""
    flattened: List[Dict[str, Any]] = []
    for ref in references:
        # Keep drawer objects as is
        if ref.get('type') in ['binnenlade', 'binnenpottenlade']:
            flattened.append(ref)
            continue
            
        # For other types, check if it's one we want to keep
        if ref.get('type') in ['baseMaterial', 'product', 'element']:
            flattened.append(ref)
        
        # Recursively flatten nested references
        if ref.get('references'):
            flattened.extend(flatten_references(ref['references']))
    
    return flattened

def flatten_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten a single entry's references"""
    if entry.get('references'):
        flattened_refs = flatten_references([ref for ref in entry['references']])
        entry['references'] = flattened_refs
    return entry

def flatten_log(input_path: Path, output_path: Path) -> None:
    """Main function to flatten the simplified log"""
    with open(input_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # Check for multiplication operations
    for entry in log_data:
        if has_multiplication(entry):
            raise ValueError("❌❌❌ Found multiplication operation in formulas. Cannot flatten log. ❌❌❌")
    
    # Flatten entries
    flattened_entries = [flatten_entry(entry) for entry in log_data]
    
    # Write flattened entries to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(flattened_entries, f, indent=2)

if __name__ == "__main__":
    input_file = Path("Logs/Current Logs/simplified_log.json")
    output_file = Path("Logs/Current Logs/flattened_log.json")
    
    try:
        flatten_log(input_file, output_file)
        print(f"✅✅✅ Flattened log created at: {output_file} ✅✅✅")
    except ValueError as e:
        print(f"Error: {e}") 