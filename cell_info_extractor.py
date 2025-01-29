from typing import Dict, List, Tuple
from pathlib import Path
from utils.excel_utils import ExcelHelper
from utils.formula_parser import FormulaParser
from utils.logging_utils import setup_logger
from utils.recursive_resolver import RecursiveResolver
from Mappings.product_mapper import ProductMapper

class CellInfoExtractor:
    """Handles extraction of cell information from Excel files."""
    
    def __init__(self, file_index: Dict[str, Path], product_mapper: ProductMapper, max_recursion_depth: int = 10):
        self.file_index = file_index
        self.max_recursion_depth = max_recursion_depth
        self.excel_helper = ExcelHelper()
        self.parser = FormulaParser()
        self.logger = setup_logger()
        self.resolver = RecursiveResolver(self, self.logger)
        self.BASE_MATERIAL_FILE = "calculatie cat 2022 .xlsx"
        self.product_mapper = product_mapper

    def extract_cell_info(self, filename: str, sheet_name: str, cell_ref: str) -> Dict:
        """Extracts formula and value from a specific cell."""
        file_path = self.file_index.get(filename)
        if not file_path:
            error_msg = f"File {filename} not found in index"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "file": filename,
                "sheet": sheet_name,
                "cell": cell_ref
            }
        
        # Create unique ID
        obj_id = f"{filename}_{sheet_name}_{cell_ref}".replace(" ", "")
        
        # Add product mapping immediately
        product_id = self.product_mapper.reverse_mapping.get(obj_id)
        
        result = {
            "id": obj_id,
            "file": filename,
            "sheet": sheet_name,
            "cell": cell_ref,
            "formula": None,
            "value": None,
            "path": str(file_path),
            "isElement": False,
            "isMultiplication": False,
            "hReferenceCount": 0,
            "isBaseMaterial": filename == self.BASE_MATERIAL_FILE,
            "isProduct": product_id is not None,
            "productID": product_id,
            "references": [],
        }
        
        try:
            formula, value = self.excel_helper.get_cell_info(file_path, sheet_name, cell_ref)
            result['formula'] = formula
            result['value'] = value
            
            if formula:
                # Check for multiplication
                result['isMultiplication'] = '*' in formula
                self.logger.debug(f"Parsing formula: {filename} {sheet_name}!{cell_ref}")
                formula_info = self.parser.parse_formula(formula, filename, sheet_name)
                result.update(formula_info)
                
                # Perform recursive resolution unless it's a multiplication
                if not result['isMultiplication']:
                    result = self.resolver.resolve_references(result, max_depth=self.max_recursion_depth)
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error processing {filename} {sheet_name}!{cell_ref}: {error_msg}")
            result['error'] = error_msg
        
        return result

    def extract_batch(self, requests: List[Tuple[str, str, str]]) -> List[Dict]:
        """Processes a batch of cell extraction requests."""
        results = []
        for filename, sheet_name, cell_ref in requests:
            result = self.extract_cell_info(filename, sheet_name, cell_ref)
            results.append(result)
        return results

    def __del__(self):
        """Clean up resources."""
        self.excel_helper.cleanup()