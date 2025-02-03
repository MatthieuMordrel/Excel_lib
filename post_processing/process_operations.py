import json
from pathlib import Path
from typing import List, Dict
import sys
# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
# Import needed types from schema
from schema.schema import LogEntry, Reference

def analyze_operations(log_path: Path, output_path: Path) -> None:
    """Analyzes a log file and generates operation statistics"""
    with open(log_path, 'r') as f:
        results: List[LogEntry] = json.load(f)  # Use LogEntry type

    stats: Dict[str, int] = {
        "total_formulas": 0,
        "has_both": 0,
        "has_multiplication": 0,
        "has_division": 0,
        "has_neither": 0
    }

    def check_references(refs: List[Reference]) -> bool:  # Use Reference type
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
        
        # Use proper FormulaResult type for references
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

def main():
    """Main entry point with simplified argument handling"""
    import sys
    default_input = Path("Logs/log.json")
    default_output = Path("Logs/operation_stats.json")
    
    # Simple argument handling without argparse
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_input
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else default_output
    
    analyze_operations(input_path, output_path)

if __name__ == "__main__":
    main() 