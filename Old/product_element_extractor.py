import json
import os
from typing import Dict, List
from schema.schema import (
    LogEntry, ProductSummary, Relationship, 
    ElementID, ProductProduct, RelationshipDict, Reference
)

def round_value(value: float, decimals: int = 3) -> float:
    """Round the value to the specified number of decimal places."""
    return round(value, decimals)

def create_element_id(ref: Reference) -> ElementID:
    """Create an element ID from a reference."""
    return {
        "elementID": f"{ref['sheet']}_{ref['cell']}_{round_value(ref['value'])}"
    }

def create_initial_relationship() -> RelationshipDict:
    """Create initial relationship structure."""
    return {
        "productProduct": [],
        "productBaseMaterial": [],
        "productElement": []
    }

def extract_relationships(log_data: List[LogEntry]) -> ProductSummary:
    """Extract relationships from the log data."""
    products: Dict[str, Relationship] = {}

    for entry in log_data:
        product_id = entry['productID']
        if product_id not in products:
            products[product_id] = {
                "productID": product_id,
                "relationships": create_initial_relationship()
            }

        for ref in entry.get('references', []):
            if ref['isProduct']:
                product_relationship: ProductProduct = {
                    "productID": ref['productID'],
                    "relationships": {
                        "productElement": [
                            create_element_id(ref)
                            for ref in ref.get('references', [])
                            if ref['isElement']
                        ],
                        "productBaseMaterial": [
                            ref['cell']
                            for ref in ref.get('references', [])
                            if ref['isBaseMaterial']
                        ]
                    }
                }
                products[product_id]["relationships"]["productProduct"].append(product_relationship)

    return {"products": list(products.values())}

def main() -> None:
    """Main function to process and save relationship data."""
    log_file_path = os.path.join('Logs', 'log.json')
    output_file_path = os.path.join('Logs', 'summary.json')

    with open(log_file_path, 'r') as log_file:
        log_data: List[LogEntry] = json.load(log_file)

    summary = extract_relationships(log_data)

    with open(output_file_path, 'w') as output_file:
        json.dump(summary, output_file, indent=2)

    print(f"Summary JSON created at {output_file_path}")

if __name__ == "__main__":
    main()
