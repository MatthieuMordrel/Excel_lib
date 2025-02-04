import re
from typing import List, Tuple
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
            "id": f"{file}_{sheet}_{cell}",
            "file": file,
            "sheet": sheet,
            "cell": cell,
            "formula": None,
            "cleaned_formula": None,
            "updated_formula": None,
            "expanded_formula": None,
            "value": None,
            "path": None,
            "isElement": False,
            "isMultiplication": False,
            "isDivision": False,
            "hReferenceCount": 0,
            "isBaseMaterial": False,
            "isProduct": False,
            "productID": None,
            "references": [],
            "error": None
        })

    def extract_references(self, cleaned_formula: str, parent_file: str, parent_sheet: str) -> Tuple[List[FormulaResult], str]:
        """
        Extracts references from a cleaned formula.
        
        Args:
            cleaned_formula (str): The cleaned formula
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            List[FormulaResult]: List of reference dictionaries
        """
        # Pattern 1: [filename]sheetname!cell (external reference)
        pattern1 = r"\[([^\]]+)\]([^\[]+)'!([A-Z]\d{1,3})"
        # Pattern 2:  
        pattern2 = r"'?([\w\s]+)'?!([A-Z]\d{1,3})"
        # Pattern 3: simple cell reference
        pattern3 = r"([A-Z]\d{1,3})"
        
        updated_formula = cleaned_formula
        
        # First, extract and remove all external references
        external_refs: List[FormulaResult] = []
        for match in re.findall(pattern1, cleaned_formula):
            file, sheet, cell = match
            if self._is_valid_cell(cell):
                external_refs.append(self._create_reference(file, sheet, cell.upper()))
                # Construct the original reference string to replace
                original_ref = f"'[{file}]{sheet}'!{cell}"
                updated_formula = updated_formula.replace(original_ref, f"{file}_{sheet}_{cell}".replace(" ", ""))

        # Remove external references from the formula
        formula_without_externals = re.sub(pattern1, "", cleaned_formula)
        
        
        # Then extract internal references
        internal_refs: List[FormulaResult] = []
        for match in re.findall(pattern2, formula_without_externals):
            sheet, cell = match
            if self._is_valid_cell(cell):
                internal_refs.append(self._create_reference(parent_file, sheet, cell.upper()))
                # Construct the original reference string to replace
                original_ref = f"'{sheet}'!{cell}" if " " in sheet else f"{sheet}!{cell}"
                updated_formula = updated_formula.replace(original_ref, f"{parent_file}_{sheet}_{cell}".replace(" ", ""))

        # Remove internal references from the formula
        formula_without_refs = re.sub(pattern2, "", formula_without_externals)
        
        
        # Finally, extract simple cell references
        simple_refs: List[FormulaResult] = []
        for match in re.findall(pattern3, formula_without_refs):
            cell = match
            if self._is_valid_cell(cell):
                simple_refs.append(self._create_reference(parent_file, parent_sheet, cell.upper()))
                # Try both formats: with and without parent sheet reference
                possible_refs = [
                    f"'{parent_sheet}'!{cell}" if " " in parent_sheet else f"{parent_sheet}!{cell}",
                    cell
                ]
                # Find which reference format actually exists in the formula
                for possible_ref in possible_refs:
                    if possible_ref in updated_formula:
                        updated_formula = updated_formula.replace(
                            possible_ref, 
                            f"{parent_file}_{parent_sheet}_{cell}".replace(" ", "")
                        )
                        break

        return external_refs + internal_refs + simple_refs, updated_formula