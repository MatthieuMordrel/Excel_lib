from pathlib import Path
import win32com.client
from typing import List, Tuple

BatchRequest = Tuple[str, str, str]  # (file_name, sheet_name, cell_ref)

def get_batch_requests(file_path: Path) -> List[BatchRequest]:
    """
    Reads batch requests from an Excel file.
    
    Args:
        file_path: Path to the Excel file containing the batch requests
        
    Returns:
        List of tuples (file, sheet, cell) for batch processing
    """
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        wb = excel.Workbooks.Open(str(file_path))
        sheet = wb.Sheets(1)
        
        # Verify columns
        headers = sheet.Range("A1:C1").Value[0]
        if headers != ('File', 'Tab', 'Cell'):
            raise ValueError("Excel file must have columns 'File', 'Tab', 'Cell' in the first row")
        
        # Read data
        batch_requests: List[BatchRequest] = []
        row = 2
        while True:
            file_name = sheet.Cells(row, 1).Value
            sheet_name = sheet.Cells(row, 2).Value
            cell_ref = sheet.Cells(row, 3).Value
            
            if not file_name or not sheet_name or not cell_ref:
                break
                
            batch_requests.append((file_name, sheet_name, cell_ref))
            row += 1
        
        wb.Close(False)
        excel.Quit()
        return batch_requests
        
    except Exception as e:
        print(f"Error reading batch requests: {str(e)}")
        raise 