import json
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_top_level_products(input_path: Path) -> List[str]:
    """
    Extracts and returns a list of unique top-level product IDs from a simplified log file.

    Args:
        input_path: Path to the simplified log file (e.g., simplified_log.json).

    Returns:
        A list of unique product IDs.
    """

    with open(input_path, 'r', encoding='utf-8') as f:
        log_data: List[Dict[str, Any]] = json.load(f)

    product_ids: List[str] = []
    seen_product_ids: set[str] = set()  # Use a set for efficient duplicate checking

    for entry in log_data:
        if entry.get("type") == "product":
            product_id = entry.get("id")
            if product_id:
                if product_id in seen_product_ids:
                    logging.warning(f"Duplicate product ID found: {product_id}")
                else:
                    product_ids.append(product_id)
                    seen_product_ids.add(product_id)

    return product_ids

def write_unique_products_to_file(product_ids:List[str], output_path: Path):
    """Writes the unique product IDs to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(product_ids, f, indent=2)

if __name__ == "__main__":
    input_file = Path("Logs/Previous Logs/External + Elements/simplified_log.")
    output_file = Path("Logs/Current Logs/unique_products.json")
    product_ids = extract_top_level_products(input_file)
    logging.info(f"Found {len(product_ids)} unique top-level products.")
    write_unique_products_to_file(product_ids, output_file)
    print(f"Unique top level products written to {output_file}") 