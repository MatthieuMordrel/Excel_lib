import json
from typing import Dict, Any, Tuple
from pathlib import Path
import pythoncom
import win32com.client

def save_to_log(result: Dict, log_path: str) -> None:
    """
    Saves extraction result to a JSON log file.
    
    Args:
        result (Dict): Dictionary containing extraction results
        log_path (str): Path to the log file
    """
    # Ensure isBaseMaterial is present in the result
    if 'isBaseMaterial' not in result:
        result['isBaseMaterial'] = result.get('file', '') == "calculatie cat 2022 .xlsx"
    
    with open(log_path, 'a') as f:
        json.dump(result, f, indent=2)
        f.write('\n')

class ExcelHelper:
    """Handles Excel operations with proper COM initialization."""
    
    def __init__(self):
        pythoncom.CoInitialize()
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = False
        self.excel.DisplayAlerts = False
        self.cache = {}

    def get_cell_info(self, file_path: Path, sheet_name: str, cell_ref: str) -> Tuple[str, Any]:
        """Extracts formula and value from a specific cell."""
        try:
            wb = self.cache.get(str(file_path))
            if wb is None:
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                wb = self.excel.Workbooks.Open(str(file_path))
                self.cache[str(file_path)] = wb
            
            sheet = wb.Sheets(sheet_name)
            if sheet is None:
                raise ValueError(f"Sheet '{sheet_name}' not found in workbook")
            
            cell = sheet.Range(cell_ref)
            if cell is None:
                raise ValueError(f"Cell '{cell_ref}' not found in sheet")
            
            return cell.Formula, cell.Value
        except Exception as e:
            raise Exception(f"Error getting cell info for {file_path} {sheet_name}!{cell_ref}: {str(e)}")

    def cleanup(self):
        """Clean up Excel resources."""
        for wb in self.cache.values():
            wb.Close(False)
        self.excel.Quit()
        pythoncom.CoUninitialize() 