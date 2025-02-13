from typing import Dict, List, Any, Set
from schema.schema import FormulaResult
from logging import Logger

class RecursiveResolver:
    """Handles recursive resolution of Excel formulas."""
    
    def __init__(self, extractor: Any, logger: Logger, stop_on_multiplication: bool):
        self.extractor = extractor
        self.logger = logger
        self.BASE_MATERIAL_FILE = "calculatie cat 2022 .xlsx"
        self.resolution_cache: Dict[str, FormulaResult] = {}
        self.stop_on_multiplication = stop_on_multiplication
        self.current_chain: Set[str] = set()  # Track current resolution chain

    def _is_base_case(self, result: FormulaResult) -> bool:
        """Determines if we should stop recursion."""
        return bool(
            result.get('isElement', False) or 
            isinstance(result.get('value'), (int, float, str)) and 
            not result.get('formula')
        )

    def _validate_reference(self, ref: FormulaResult) -> bool:
        """Validates if a reference contains all required fields."""
        return all(key in ref for key in ['file', 'sheet', 'cell'])


    def _classify_cell(self, result: FormulaResult) -> str:
        """Determine cell classification for logging"""
        if result.get('isProduct'):
            return 'Product'
        if result.get('isElement'):
            return 'Element'
        if result.get('isBaseMaterial'):
            return 'Base Material'
        return 'Other'

    def resolve_references(self, result: FormulaResult, max_depth: int = 10, current_depth: int = 0) -> FormulaResult:
        """Recursively resolves formula references."""
        if current_depth >= max_depth:
            self.logger.warning(f"Max recursion depth {max_depth} reached for {result['id']}")
            result['error'] = "Max Recursion Depth Error: Max recursion depth reached"
            return result
        # Add classification logging at resolution start
        
        cache_key = f"{result['file']}|{result['sheet']}|{result['cell']}"
        
        if cache_key in self.current_chain:
            self.logger.error(f"Circular reference detected: {cache_key}")
            result['error'] = "Circular Error: Circular reference detected"
            return result
        
        self.current_chain.add(cache_key)
        try:
            if cache_key in self.resolution_cache:
                return self.resolution_cache[cache_key]
            
            if self._is_base_case(result):
                return result
            
            # Process references
            resolved_references: List[FormulaResult] = []
            for ref in result.get('references', []):
                if self._validate_reference(ref):
                    # Log when resolving a reference
                    resolved_ref = self.extractor.extract_cell_info(ref['file'], ref['sheet'], ref['cell'])
                    resolved_references.append(resolved_ref)
            
            result['references'] = resolved_references
            
            # Store before returning
            self.resolution_cache[cache_key] = result
            return result
        finally:
            self.current_chain.remove(cache_key) 