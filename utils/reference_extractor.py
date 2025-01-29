import re
from typing import List, Dict

class ReferenceExtractor:
    """Handles extraction of references from cleaned formulas."""
    
    @staticmethod
    def _is_valid_cell(cell_ref: str) -> bool:
        """
        Validates if a cell reference is in the correct format.
        
        Args:
            cell_ref (str): The cell reference to validate
            
        Returns:
            bool: True if the cell reference is valid
        """
        # Pattern: One or more letters followed by 1 to 3 digits
        cell_pattern = r"^[A-Z]\d{1,3}$"
        return bool(re.match(cell_pattern, cell_ref))
    
    def extract_references(self, cleaned_formula: str, parent_file: str, parent_sheet: str) -> List[Dict]:
        """
        Extracts references from a cleaned formula.
        
        Args:
            cleaned_formula (str): The cleaned formula
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            List[Dict]: List of reference dictionaries
        """
        # Pattern 1: [filename]sheetname!cell (external reference)
        pattern1 = r"\[([^\]]+)\]([^\[]+)'!([A-Z]\d{1,3})"
        # Pattern 2: sheetname!cell (internal reference)
        pattern2 = r"'?([\w\s]+)'?!([A-Z]\d{1,3})"
        # Pattern 3: simple cell reference
        pattern3 = r"([A-Z]\d{1,3})"
        
        references = []
        matched_cells = set()
        
        # First, extract and remove all external references
        external_refs = []
        for match in re.findall(pattern1, cleaned_formula):
            file, sheet, cell = match
            if cell not in matched_cells and self._is_valid_cell(cell):
                external_refs.append({
                    "file": file,
                    "sheet": sheet,
                    "cell": cell.upper()
                })
                matched_cells.add(cell)
        
        # Remove external references from the formula
        formula_without_externals = re.sub(pattern1, "", cleaned_formula)
        print(formula_without_externals)
        
        # Then extract internal references
        internal_refs = []
        for match in re.findall(pattern2, formula_without_externals):
            sheet, cell = match
            if cell not in matched_cells and self._is_valid_cell(cell):
                internal_refs.append({
                    "file": parent_file,
                    "sheet": sheet,
                    "cell": cell.upper()
                })
                matched_cells.add(cell)
        
        # Remove internal references from the formula
        formula_without_refs = re.sub(pattern2, "", formula_without_externals)
        print(formula_without_refs)
        
        # Finally, extract simple cell references
        simple_refs = []
        for match in re.findall(pattern3, formula_without_refs):
            cell = match
            if cell not in matched_cells and self._is_valid_cell(cell):
                simple_refs.append({
                    "file": parent_file,
                    "sheet": parent_sheet,
                    "cell": cell.upper()
                })
                matched_cells.add(cell)
        
        return external_refs + internal_refs + simple_refs 