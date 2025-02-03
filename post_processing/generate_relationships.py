import json
from pathlib import Path
from typing import List, Dict, Any
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

def load_processed_log(log_path: Path) -> List[Dict[str, Any]]:
    """Load and return the processed log data"""
    try:
        if not log_path.exists():
            raise FileNotFoundError(f"Processed log file not found: {log_path}")
        with open(log_path, 'r') as f:
            print(f"✅ Successfully loaded processed log from {log_path}")
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading processed log: {e}")
        raise

def process_product(product: Dict[str, Any], product_id: str, 
                    p_p_relations: List[Dict[str, str]],
                    p_e_relations: List[Dict[str, str]],
                    p_bm_relations: List[Dict[str, str]]) -> None:
    """
    Process a product and its references to extract relationships.
    Stops recursion when encountering a product, element, or base material.
    """
    try:
        for ref in product.get('references', []):
            if ref.get('isProduct'):
                p_p_relations.append({
                    'Product_Id': product_id,
                    'Product_Id_Child': ref.get('productID', '')
                })
                print(f"➕ Added P_P relationship: {product_id} -> {ref.get('productID', '')}")
                continue
                
            if ref.get('isElement'):
                element_id = f"{ref.get('sheet', '')}_{round(ref.get('value', 0), 3)}"
                p_e_relations.append({
                    'Product_Id': product_id,
                    'Element_Id': element_id
                })
                print(f"➕ Added P_E relationship: {product_id} -> {element_id}")
                continue
                
            if ref.get('isBaseMaterial'):
                p_bm_relations.append({
                    'Product_Id': product_id,
                    'BM_Cell': f"{ref.get('sheet', '')}!{ref.get('cell', '')}"
                })
                print(f"➕ Added P_BM relationship: {product_id} -> {ref.get('sheet', '')}!{ref.get('cell', '')}")
                continue
                
            process_product(ref, product_id, p_p_relations, p_e_relations, p_bm_relations)
    except Exception as e:
        print(f"❌ Error processing product {product_id}: {e}")
        raise

def update_excel_sheet(sheet: Worksheet, data: List[Dict[str, str]], headers: List[str]) -> None:
    """
    Update an Excel sheet with new data while preserving existing content.
    Adds new rows below existing data.
    """
    try:
        start_row = sheet.max_row + 1 if sheet.max_row > 1 else 2
        print(f"📝 Updating sheet {sheet.title} starting at row {start_row}")
        
        for i, row in enumerate(data, start=start_row):
            for j, header in enumerate(headers, start=1):
                sheet.cell(row=i, column=j, value=row.get(header, ''))
        print(f"✅ Successfully updated {len(data)} rows in sheet {sheet.title}")
    except Exception as e:
        print(f"❌ Error updating sheet {sheet.title}: {e}")
        raise

def generate_relationships(log_path: Path, excel_path: Path) -> None:
    """
    Main function to generate relationships and update the Excel file.
    """
    try:
        print("\n🚀 Starting relationship generation process")
        
        # Load processed log data
        data = load_processed_log(log_path)
        print(f"📊 Found {len(data)} entries in processed log")
        
        # Initialize relationship containers
        p_p_relations: List[Dict[str, str]] = []
        p_e_relations: List[Dict[str, str]] = []
        p_bm_relations: List[Dict[str, str]] = []
        
        # Process each root object
        product_count = 0
        for item in data:
            if item.get('isProduct'):
                product_count += 1
                product_id = item.get('productID', '')
                print(f"\n🔍 Processing product {product_id}")
                process_product(item, product_id, p_p_relations, p_e_relations, p_bm_relations)
        
        print(f"\n📊 Found {product_count} products with relationships")
        print(f"  - Product-Product relationships: {len(p_p_relations)}")
        print(f"  - Product-Element relationships: {len(p_e_relations)}")
        print(f"  - Product-BaseMaterial relationships: {len(p_bm_relations)}")
        
        # Load existing Excel workbook
        try:
            workbook = openpyxl.load_workbook(excel_path)
            print(f"📂 Successfully loaded Excel workbook from {excel_path}")
        except Exception as e:
            print(f"❌ Error loading Excel workbook: {e}")
            raise
        
        # Update each sheet with the corresponding relationships
        update_excel_sheet(workbook['P_P'], p_p_relations, ['Product_Id', 'Product_Id_Child'])
        update_excel_sheet(workbook['P_E'], p_e_relations, ['Product_Id', 'Element_Id'])
        update_excel_sheet(workbook['P_BM'], p_bm_relations, ['Product_Id', 'BM_Cell'])
        
        # Save the updated workbook
        try:
            workbook.save(excel_path)
            print(f"💾 Successfully saved updated workbook to {excel_path}")
        except Exception as e:
            print(f"❌ Error saving workbook: {e}")
            raise
        
        print("\n🎉 Relationship generation completed successfully!")
        
    except Exception as e:
        print(f"\n❌❌❌ Error in relationship generation: {e}")
        raise

if __name__ == "__main__":
    try:
        # Define paths
        log_path = Path(__file__).parent / "processed_log.json"
        excel_path = Path(__file__).parent / "Relationships.xlsx"
        
        print(f"📄 Log file path: {log_path}")
        print(f"📊 Excel file path: {excel_path}")
        
        # Generate and update relationships
        generate_relationships(log_path, excel_path)
    except Exception as e:
        print(f"\n❌❌❌ Fatal error: {e}") 