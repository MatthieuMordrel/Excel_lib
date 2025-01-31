from typing import List, Dict
from schema.schema import FormulaResult

class ElementDetector:
    """Handles detection of element formulas based on references."""
    
    @staticmethod
    def is_element(references: List[FormulaResult]) -> bool:
        """
        Determines if the formula represents an element based on references.
        
        Args:
            references (List[FormulaResult]): List of reference dictionaries
            
        Returns:
            bool: True if formula contains at least 4 H-references in the same sheet
        """
        # Filter for H-references
        h_references = [ref for ref in references if ref["cell"].startswith('H')]
        
        # Group H-references by sheet
        sheet_counts: Dict[str, int] = {}
        for ref in h_references:
            sheet_counts[ref["sheet"]] = sheet_counts.get(ref["sheet"], 0) + 1
        
        # Check if any sheet has at least 4 H-references
        return any(count >= 4 for count in sheet_counts.values()) 