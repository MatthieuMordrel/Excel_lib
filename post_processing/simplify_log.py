import json
from pathlib import Path
from typing import Dict, Any

def process_entry(entry: Dict[str, Any], is_top: bool = True) -> Dict[str, Any]:
    """Process individual log entry to extract required properties"""
    return {
        "type": "product" if entry.get("isProduct", False) else "element" if entry.get("isElement", False) else "baseMaterial" if entry.get("isBaseMaterial", False) else "none",
        "file": entry.get("file"),
        "sheet": entry.get("sheet"),
        "cell": entry.get("cell"),
        "cleaned_formula": entry.get("cleaned_formula"),
        "id": entry.get("productID") if entry.get("isProduct", False) else f"{entry.get('sheet')}_{round(entry.get('value', 0), 3)}" if entry.get("isElement",True) else entry.get("cell") if entry.get("isBaseMaterial",False) else None,
        "references": [process_entry(ref, False) for ref in entry.get("references", [])] if (not entry.get("isProduct", False) or is_top) else None
    }


def simplify_log(input_path: Path, output_path: Path) -> None:
    """Main processing function"""
    with open(input_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # True will be sent for every top object we processin log_data
    simplified = [process_entry(entry, True) for entry in log_data]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, indent=2)

if __name__ == "__main__":
    input_file = Path("Logs/log.json")
    output_file = Path("Logs/simplified_log.json")
    
    simplify_log(input_file, output_file)
    print(f"Simplified log created at: {output_file}") 