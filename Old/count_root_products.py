import json
from pathlib import Path
from typing import Dict, List, TypedDict


class Stats(TypedDict):
    total_root_products: int
    products_by_sheet: Dict[str, int]
    unique_product_ids: List[str]

def count_root_products(log_path: Path) -> Stats:
    """
    Count the number of root products and gather statistics from the processed log.
    
    Returns:
        Dict containing:
        - total_root_products: Total number of root products
        - products_by_sheet: Dictionary with sheet names as keys and product counts as values
        - unique_product_ids: Set of unique product IDs
    """
    try:
        # Load the processed log data
        with open(log_path, 'r') as f:
            data = json.load(f)
            
        # Initialize counters with explicit types
        stats: Stats = {
            'total_root_products': 0,
            'products_by_sheet': {},
            'unique_product_ids': []
        }
        
        # Process each root object
        for item in data:
            if item.get('isProduct'):
                total_products: int = stats['total_root_products']
                stats['total_root_products'] = total_products + 1
                
                # Count products by sheet
                sheet = item.get('sheet', 'Unknown')
                stats['products_by_sheet'][sheet] = stats['products_by_sheet'].get(sheet, 0) + 1
                
                # Track unique product IDs
                if item.get('productID'):
                    stats['unique_product_ids'].append(item['productID'])
        
        return stats
        
    except Exception as e:
        print(f"❌ Error processing log file: {e}")
        raise

def print_stats(stats: Stats) -> None:
    """Print the statistics in a formatted way"""
    print("\n📊 Root Products Statistics:")
    print(f"{'='*50}")
    print(f"Total root products: {stats['total_root_products']}")
    print(f"Unique product IDs: {len(stats['unique_product_ids'])}")
    print("\nProducts by sheet:")
    print(f"{'-'*50}")
    for sheet, count in stats['products_by_sheet'].items():
        print(f"  {sheet}: {count}")

def save_stats(stats: Stats, output_path: Path) -> None:
    """Save the statistics to a JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\n✅ Statistics saved to {output_path}")
    except Exception as e:
        print(f"❌ Error saving statistics: {e}")
        raise

if __name__ == "__main__":
    try:
        # Define paths
        log_path = Path(__file__).parent / "processed_log.json"
        output_path = Path(__file__).parent / "root_products_stats.json"
        
        print(f"📄 Processing log file: {log_path}")
        
        # Generate statistics
        stats = count_root_products(log_path)
        
        # Print statistics
        print_stats(stats)
        
        # Save statistics
        save_stats(stats, output_path)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}") 