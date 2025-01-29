from typing import Dict, List, Any
import logging

class RecursiveResolver:
    """Handles recursive resolution of Excel formulas."""
    
    def __init__(self, extractor: Any, logger: logging.Logger):
        self.extractor = extractor
        self.logger = logger
        self.BASE_MATERIAL_FILE = "calculatie cat 2022 .xlsx"

    def _is_base_case(self, result: Dict) -> bool:
        """Determines if we should stop recursion."""
        return (result.get('isElement', False) or 
                result.get('isMultiplication', False) or
                isinstance(result.get('value'), (int, float, str)) and 
                not result.get('formula'))

    def _validate_reference(self, ref: Dict) -> bool:
        """Validates if a reference contains all required fields."""
        return all(key in ref for key in ['file', 'sheet', 'cell'])

    def resolve_references(self, result: Dict, max_depth: int = 10) -> Dict:
        """Resolves references recursively."""
        if self._is_base_case(result):
            return result
        
        # Process references
        resolved_references = []
        for ref in result.get('references', []):
            if self._validate_reference(ref):
                # Log when resolving a reference
                self.logger.debug(f"Resolving reference: {ref['file']} {ref['sheet']}!{ref['cell']}")
                resolved_ref = self.extractor.extract_cell_info(ref['file'], ref['sheet'], ref['cell'])
                resolved_references.append(resolved_ref)
            
        result['references'] = resolved_references
        return result 