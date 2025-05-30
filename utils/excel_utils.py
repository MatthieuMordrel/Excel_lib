import json
from typing import Dict, Any, Tuple
from pathlib import Path
import pythoncom
import win32com.client
from utils.logging_utils import setup_logger
from openpyxl import load_workbook
from collections import OrderedDict
from openpyxl.workbook.workbook import Workbook
from win32com.client import CDispatch  # For Excel workbook type

def save_to_log(result: Dict[str, Any], log_path: str) -> None:
    """
    Saves extraction result to a JSON log file.
    
    Args:
        result (Dict): Dictionary containing extraction results
        log_path (str): Path to the log file
    """
    
    with open(log_path, 'a') as f:
        json.dump(result, f, indent=2)
        f.write('\n')

class ExcelHelper:
    """Handles Excel operations with proper COM initialization."""
    
    def __init__(self):
        pythoncom.CoInitialize()
        self.excel = win32com.client.gencache.EnsureDispatch("Excel.Application")
        try:
            # Some Excel versions might restrict changing visibility
            self.excel.Visible = False
        except AttributeError:
            # If visibility can't be set, continue anyway
            pass
        self.excel.DisplayAlerts = False
        self.excel.AskToUpdateLinks = False
        self.excel.AlertBeforeOverwriting = False
        self.cache: Dict[str, CDispatch] = {}  # Cache of Excel workbooks
        self.logger = setup_logger()  # Initialize the logger

    def get_cell_info(self, file_path: Path, sheet_name: str, cell_ref: str) -> Tuple[str, Any]:
        """Extracts formula and value from a specific cell."""
        try:
            wb = self.cache.get(str(file_path))
            if wb is None:
                if not file_path.exists():
                    self.logger.warning(f"File not found: {file_path}")
                    return "File not found", None  # Return directly for file not found
                wb = self.excel.Workbooks.Open(str(file_path))
                self.cache[str(file_path)] = wb
            
            sheet = wb.Sheets(sheet_name)
            if sheet is None:
                self.logger.warning(f"Sheet not found: {sheet_name} in {file_path}")
                return "Sheet not found", None  # Return directly for sheet not found
            
            cell = sheet.Range(cell_ref)
            if cell is None:
                self.logger.warning(f"Cell not found: {cell_ref} in {sheet_name}")
                return "Cell not found", None  # Return directly for cell not found
            
            # Check if the cell has a formula
            if not cell.HasFormula:
                self.logger.warning(f"Cell has no formula: {cell_ref} in {sheet_name}")
                return "Cell has no formula in file", cell.Value  # Return message if no formula
            
            return cell.Formula, cell.Value
        except Exception as e:
            error_message = f"Error: {str(e)}"
            self.logger.error(error_message)
            return error_message, None

    def cleanup(self):
        """Clean up Excel resources."""
        for wb in self.cache.values():
            wb.Close(False)
        self.excel.Quit()
        pythoncom.CoUninitialize()

class ExcelUtils:
    """Add LRU workbook caching with max size"""
    _WORKBOOK_CACHE: OrderedDict[str, Workbook] = OrderedDict()
    MAX_CACHE_SIZE = 20  # Adjust based on available memory

    @classmethod
    def get_workbook(cls, file_path: Path) -> Workbook:
        """Get cached workbook or load new one"""
        key = str(file_path)
        
        # Get from cache if exists
        if key in cls._WORKBOOK_CACHE:
            cls._WORKBOOK_CACHE.move_to_end(key)
            return cls._WORKBOOK_CACHE[key]
        
        # Load new workbook with optimizations
        wb = load_workbook(
            filename=file_path,
            read_only=True,  # Dramatically faster loading
            data_only=True,  # Only needed for values
            keep_links=False  # Reduce external link loading
        )
        
        # Manage cache size
        if len(cls._WORKBOOK_CACHE) >= cls.MAX_CACHE_SIZE:
            cls._WORKBOOK_CACHE.popitem(last=False)
            
        cls._WORKBOOK_CACHE[key] = wb
        return wb 