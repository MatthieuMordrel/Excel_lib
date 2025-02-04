from .reference_extractor import ReferenceExtractor
from .element_detector import ElementDetector
from schema.schema import FormulaInfo
from .add_quantity import AddQuantity

class FormulaParser:
    """Main parser that coordinates the formula parsing process."""
    
    def __init__(self):
        self.extractor = ReferenceExtractor()
        self.detector = ElementDetector()
        self.add_quantity = AddQuantity()
    
    def parse_formula(self, cleaned_formula: str, parent_file: str, parent_sheet: str) -> FormulaInfo:
        """
        Parses a cleaned Excel formula to extract references and determine if it's an element.
        
        Args:
            cleaned_formula (str): The cleaned Excel formula to parse
            parent_file (str): The file containing the formula
            parent_sheet (str): The sheet containing the formula
            
        Returns:
            FormulaInfo: Information about the formula
        """
        if not cleaned_formula:
            return FormulaInfo({
                "isElement": False,
                "hReferenceCount": 0,
                "isBaseMaterial": False,
                "isProduct": False,
                "updated_formula": None,
                "expanded_formula": None,
                "references": []
            })
        
        # Extract references from the cleaned formula
        references, updated_formula = self.extractor.extract_references(cleaned_formula, parent_file, parent_sheet)
        print("Updated formula: ", updated_formula)
        
        # Determine if it's an element
        is_element = self.detector.is_element(references)

        # Add the quantity to the references
        # expanded_formula = self.add_quantity.simpy_formula(updated_formula)

        # Count H-references
        h_reference_count = len([ref for ref in references if ref["cell"].startswith('H')])

        return FormulaInfo({
            "isElement": is_element,
            "hReferenceCount": h_reference_count,
            "isBaseMaterial": False,
            "isProduct": False,
            "updated_formula": updated_formula,
            "expanded_formula": None,
            "references": references


        })