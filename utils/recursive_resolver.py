from typing import Dict, List, Any
import logging
from utils.logging_utils import log_request_completion

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

    def resolve_references(self, result: Dict, depth: int = 0, max_depth: int = 10) -> Dict:
        """Recursively resolves formula references."""
        self.logger.debug(f"Resolving {result['file']} {result['sheet']}!{result['cell']} at depth {depth}/{max_depth}")
        
        if depth >= max_depth:
            result['error'] = f'Maximum recursion depth reached ({max_depth})'
            self.logger.warning(f"Max depth reached for {result['file']} {result['sheet']}!{result['cell']}")
            return result
            
        if self._is_base_case(result):
            self.logger.debug(f"Base case reached for {result['file']} {result['sheet']}!{result['cell']}")
            # Clean up references if it's an element or base material
            if result.get('isElement', False) or result.get('isBaseMaterial', False):
                result.pop('references', None)
            return result

        resolved_references = []
        for ref in result.get('references', []):
            if not self._validate_reference(ref):
                self.logger.warning(f"Invalid reference format: {ref}")
                continue
                
            # Create ID for reference
            ref_id = f"{ref['file']}_{ref['sheet']}_{ref['cell']}".replace(" ", "")
            ref['id'] = ref_id
            ref['isBaseMaterial'] = ref['file'] == self.BASE_MATERIAL_FILE
            
            self.logger.debug(f"Processing reference: {ref['file']} {ref['sheet']}!{ref['cell']}")
            try:
                ref_result = self.extractor.extract_cell_info(
                    ref['file'],
                    ref['sheet'],
                    ref['cell']
                )
                resolved_ref = self.resolve_references(ref_result, depth + 1, max_depth)
                resolved_references.append(resolved_ref)
            except Exception as e:
                self.logger.error(f"Error processing reference {ref['file']} {ref['sheet']}!{ref['cell']}: {str(e)}")
                resolved_references.append({
                    "error": str(e),
                    **ref
                })

        # Update the references in place instead of creating a new property
        result['references'] = resolved_references
        log_request_completion(self.logger, result)
        return result 