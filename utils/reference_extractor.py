import re
from typing import List, Set
from schema.schema import FormulaResult

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
    
    def _create_reference(self, file: str, sheet: str, cell: str) -> FormulaResult:
        """Create a properly typed reference."""
        return FormulaResult({
            "id": None,
            "file": file,
            "sheet": sheet,
            "cell": cell,
            "formula": None,
            "cleaned_formula": None,
            "updated_formula": None,
            "value": None,
            "path": None,
            "productID": None,
            "isProduct": False,
            "isBaseMaterial": False,
            "isElement": False,
            "isMultiplication": False,
            "isDivision": False,
            "hReferenceCount": 0,
            "references": [],
            "error": None
        })

    def extract_references(self, cleaned_formula: str, parent_file: str, parent_sheet: str) -> tuple[List[FormulaResult], str]:
        """
        Extracts references from a cleaned formula and creates an updated formula with reference IDs.
        
        Args:
            cleaned_formula (str): The cleaned formula
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            tuple[List[FormulaResult], str]: List of reference dictionaries and updated formula
        """
        # Pattern 1: [filename]sheetname!cell (external reference)
        pattern1 = r"\[([^\]]+)\]([^\[]+)'!([A-Z]\d{1,3})"
        # Pattern 2: sheetname!cell (internal reference)
        pattern2 = r"'?([\w\s]+)'?!([A-Z]\d{1,3})"
        # Pattern 3: simple cell reference
        pattern3 = r"([A-Z]\d{1,3})"
        
        updated_formula = cleaned_formula
        matched_cells: Set[str] = set()
        
        # First, extract and remove all external references
        external_refs: List[FormulaResult] = []
        for match in re.finditer(pattern1, cleaned_formula):
            file, sheet, cell = match.groups()
            if cell not in matched_cells and self._is_valid_cell(cell):
                ref = self._create_reference(file, sheet, cell.upper())
                external_refs.append(ref)
                matched_cells.add(cell)
                # Replace the full match with the reference ID
                updated_formula = updated_formula.replace(match.group(0),f"{ref['file']}_{ref['sheet']}_{ref['cell']}".replace(" ", ""))

        # Then extract internal references
        internal_refs: List[FormulaResult] = []
        for match in re.finditer(pattern2, updated_formula):
            sheet, cell = match.groups()
            if cell not in matched_cells and self._is_valid_cell(cell):
                ref = self._create_reference(parent_file, sheet, cell.upper())
                internal_refs.append(ref)
                matched_cells.add(cell)
                # Replace the full match with the reference ID
                updated_formula = updated_formula.replace(match.group(0),f"{ref['file']}_{ref['sheet']}_{ref['cell']}".replace(" ", ""))

        # Finally, extract simple cell references
        simple_refs: List[FormulaResult] = []
        for match in re.finditer(pattern3, updated_formula):
            cell = match.group(1)
            if cell not in matched_cells and self._is_valid_cell(cell):
                ref = self._create_reference(parent_file, parent_sheet, cell.upper())
                simple_refs.append(ref)
                matched_cells.add(cell)
                # Replace the full match with the reference ID
                updated_formula = updated_formula.replace(match.group(0),f"{ref['file']}_{ref['sheet']}_{ref['cell']}".replace(" ", ""))

        return external_refs + internal_refs + simple_refs, updated_formula 