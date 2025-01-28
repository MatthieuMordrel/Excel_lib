import win32com.client
from typing import Dict, List, Tuple
from pathlib import Path
from utils.formula_parser import FormulaParser

class CellInfoExtractor:
    """Handles extraction of cell information from Excel files with caching."""
    
    def __init__(self, file_index: Dict[str, Path]):
        self.file_index = file_index
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = False
        self.excel.DisplayAlerts = False
        self.cache = {}  # Cache for open workbooks
        self.parser = FormulaParser()  # Create an instance of FormulaParser
    
    def get_cell_formula_and_value(self, sheet, cell_ref):
        """
        Extracts formula and value from a specific cell in an Excel sheet.
        """
        cell = sheet.Range(cell_ref)
        return cell.Formula, cell.Value
    
    def extract_cell_info(self, filename: str, sheet_name: str, cell_ref: str) -> Dict:
        """
        Extracts formula and value from a specific cell in an Excel file.
        Uses caching to avoid reopening the same file multiple times.
        """
        file_path = self.file_index.get(filename)
        if not file_path:
            return {
                "error": f"File {filename} not found in index",
                "file": filename,
                "sheet": sheet_name,
                "cell": cell_ref
            }
        
        result = {
            "file": filename,
            "sheet": sheet_name,
            "cell": cell_ref,
            "formula": None,
            "value": None,
            "path": str(file_path),
            "isElement": False,
            "references": [],
            "hReferenceCount": 0
        }
        
        try:
            # Get workbook from cache or open it
            wb = self.cache.get(str(file_path))
            if wb is None:
                wb = self.excel.Workbooks.Open(str(file_path))
                self.cache[str(file_path)] = wb
            
            sheet = wb.Sheets(sheet_name)
            formula, value = self.get_cell_formula_and_value(sheet, cell_ref)
            result['formula'] = formula
            result['value'] = value
            
            # Parse the formula with parent context
            if formula:
                formula_info = self.parser.parse_formula(formula, filename, sheet_name)
                result.update(formula_info)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def extract_batch(self, requests: List[Tuple[str, str, str]]) -> List[Dict]:
        """
        Processes multiple cell extraction requests efficiently.
        
        Args:
            requests: List of tuples (filename, sheet_name, cell_ref)
        
        Returns:
            List of result dictionaries
        """
        # Group requests by file
        file_groups = {}
        for idx, (filename, sheet_name, cell_ref) in enumerate(requests):
            if filename not in file_groups:
                file_groups[filename] = []
            file_groups[filename].append((sheet_name, cell_ref, idx))
        
        results = [None] * len(requests)
        
        # Process each file's requests together
        for filename, file_requests in file_groups.items():
            file_path = self.file_index.get(filename)
            if not file_path:
                for _, _, idx in file_requests:
                    results[idx] = {
                        "error": f"File {filename} not found in index",
                        "file": filename,
                        "sheet": sheet_name,
                        "cell": cell_ref
                    }
                continue
            
            try:
                # Get workbook from cache or open it
                wb = self.cache.get(str(file_path))
                if wb is None:
                    wb = self.excel.Workbooks.Open(str(file_path))
                    self.cache[str(file_path)] = wb
                
                # Process all requests for this file
                for sheet_name, cell_ref, idx in file_requests:
                    result = {
                        "file": filename,
                        "sheet": sheet_name,
                        "cell": cell_ref,
                        "formula": None,
                        "value": None,
                        "path": str(file_path)
                    }
                    try:
                        sheet = wb.Sheets(sheet_name)
                        formula, value = self.get_cell_formula_and_value(sheet, cell_ref)
                        result['formula'] = formula
                        result['value'] = value
                        
                        # Parse the formula with parent context
                        if formula:
                            formula_info = self.parser.parse_formula(formula, filename, sheet_name)
                            result.update(formula_info)
                    except Exception as e:
                        result['error'] = str(e)
                    results[idx] = result
            except Exception as e:
                # Mark all requests for this file as error
                for _, _, idx in file_requests:
                    results[idx] = {
                        "error": f"File error: {str(e)}",
                        "file": filename,
                        "sheet": sheet_name,
                        "cell": cell_ref
                    }
        
        return results
    
    def __del__(self):
        """Clean up Excel application and close all cached workbooks."""
        for wb in self.cache.values():
            wb.Close(False)
        self.excel.Quit()