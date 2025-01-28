from typing import Dict
from .formula_cleaner import FormulaCleaner
from .reference_extractor import ReferenceExtractor
from .element_detector import ElementDetector

class FormulaParser:
    """Main parser that coordinates the formula parsing process."""
    
    def __init__(self):
        self.cleaner = FormulaCleaner()
        self.extractor = ReferenceExtractor()
        self.detector = ElementDetector()
    
    def parse_formula(self, formula: str, parent_file: str, parent_sheet: str) -> Dict:
        """
        Parses an Excel formula to extract references and determine if it's an element.
        
        Args:
            formula (str): The Excel formula to parse
            file_path (str): The file path containing the formula
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            Dict: Dictionary containing:
                - isElement: True if formula contains at least 4 H-references in the same sheet
                - references: List of dicts with file, sheet, cell for each reference
                - hReferenceCount: Number of H-references found
                - cleaned_formula: The cleaned version of the formula
        """
        # Clean the formula
        cleaned_formula = self.cleaner.clean_formula(formula)
        
        if not cleaned_formula:
            return {
                "isElement": False,
                "references": [],
                "hReferenceCount": 0,
                "cleaned_formula": cleaned_formula
            }
        
        # Return List[Dict]: List of reference dictionaries
        #Example: [{'file': '2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx', 'sheet': 'OVERZICHT COZ1323', 'cell': 'C33'}]
        references = self.extractor.extract_references(cleaned_formula, parent_file, parent_sheet)
        
        # Determine if it's an element
        is_element = self.detector.is_element(references)
        
        # Count H-references
        h_reference_count = len([ref for ref in references if ref["cell"].startswith('H')])
        
        return {
            "isElement": is_element,
            "references": references,
            "hReferenceCount": h_reference_count,
            "cleaned_formula": cleaned_formula
        }