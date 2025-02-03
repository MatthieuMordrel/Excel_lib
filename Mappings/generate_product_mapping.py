import json
from pathlib import Path
import win32com.client

def generate_product_mapping(excel_path: Path, output_path: Path) -> None:
    """
    Generates a JSON product mapping from an Excel file.
    
    Args:
        excel_path: Path to the Excel file containing product mapping
        output_path: Path to save the JSON file
    """
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        wb = excel.Workbooks.Open(str(excel_path))
        sheet = wb.Sheets("All Products")
        
        # Verify columns
        headers = sheet.Range("A1:F1").Value[0]
        expected_headers = ('Code', 'Price Group', 'Product_ID', 'File', 'Tab', 'Cell')
        if headers != expected_headers:
            raise ValueError("Excel file must have columns 'Code', 'Price Group', 'Product_ID', 'File', 'Tab', 'Cell'")
        
        # Create mapping dictionary
        product_mapping = {}
        row = 2
        while True:
            values = sheet.Range(f"A{row}:F{row}").Value[0]
            if not any(values):  # Stop if row is empty
                break
                
            _, _, product_id, file, tab, cell = values
            
            # Ensure .xlsx extension is present
            if not file.lower().endswith('.xlsx'):
                file += '.xlsx'
            
            # Create key in format Product_ID: "file_tab_cell" with no spaces
            concatenated = f"{file}_{tab}_{cell}"
            product_mapping[product_id] = concatenated.replace(" ", "")
            
            row += 1
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(product_mapping, f, indent=2)
        
        wb.Close(False)
        excel.Quit()
        print(f"Successfully generated product mapping at {output_path}")
        
    except Exception as e:
        print(f"Error generating product mapping: {str(e)}")
        raise

if __name__ == "__main__":
    # Navigate back one folder and then into the "Batch File" directory
    batch_file_path = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Scripts\Project\Batch File\File - Tab - Cell - (start of recursive resolver) - New.xlsx")

    # Print the full path
    print(batch_file_path.resolve())
    
    # Example usage
    excel_path = batch_file_path
    output_path = Path("Mappings/product_mapping.json")
    generate_product_mapping(excel_path, output_path) 