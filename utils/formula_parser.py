from typing import Dict
from .reference_extractor import ReferenceExtractor
from .element_detector import ElementDetector

class FormulaParser:
    """Main parser that coordinates the formula parsing process."""
    
    def __init__(self):
        self.extractor = ReferenceExtractor()
        self.detector = ElementDetector()
    
    def parse_formula(self, cleaned_formula: str, parent_file: str, parent_sheet: str) -> Dict:
        """
        Parses a cleaned Excel formula to extract references and determine if it's an element.
        
        Args:
            cleaned_formula (str): The cleaned Excel formula to parse
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            Dict: Dictionary containing:
                - isElement: True if formula contains at least 4 H-references in the same sheet
                - references: List of dicts with file, sheet, cell for each reference
                - hReferenceCount: Number of H-references found
        """
        if not cleaned_formula:
            return {
                "isElement": False,
                "hReferenceCount": 0,
                "references": [],
            }
        
        # Extract references from the cleaned formula
        references = self.extractor.extract_references(cleaned_formula, parent_file, parent_sheet)
        
        # Determine if it's an element
        is_element = self.detector.is_element(references)
        
        # Count H-references
        h_reference_count = len([ref for ref in references if ref["cell"].startswith('H')])
        
        return {
            "isElement": is_element,
            "hReferenceCount": h_reference_count,
            "references": references,
        }