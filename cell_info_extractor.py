from typing import Dict, List, Tuple
from pathlib import Path
from utils.excel_utils import ExcelHelper, ExcelUtils
from utils.formula_parser import FormulaParser
from utils.formula_cleaner import FormulaCleaner
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
        self.cleaner = FormulaCleaner()
        self.logger = setup_logger()
        self.resolver = RecursiveResolver(self, self.logger)
        self.BASE_MATERIAL_FILE = "calculatie cat 2022 .xlsx"
        self.product_mapper = product_mapper

    def extract_batch(self, requests: List[Tuple[str, str, str]]) -> List[Dict]:
        """Processes a batch of cell extraction requests."""
        results = []
        for file_name, sheet_name, cell_ref in requests:
            result = self.extract_cell_info(file_name, sheet_name, cell_ref)
            results.append(result)
        return results

    def extract_cell_info(self, filename: str, sheet_name: str, cell_ref: str) -> Dict:
        """Extracts formula and value from a specific cell."""
        # Create unique ID for the cell
        id = f"{filename}_{sheet_name}_{cell_ref}".replace(" ", "")
        self.logger.debug(f"Extracting cell info: {id}")
        obj_id = id
        
        file_path = self.file_index.get(filename)
        if not file_path:
            error_msg = f"File {filename} not found in index"
            self.logger.error(error_msg)
            return {
                "id": id,
                "file": filename,
                "sheet": sheet_name,
                "cell": cell_ref,
                "formula": "File not found",
                "cleaned_formula": None,
                "value": None,
                "path": None,
                "isElement": False,
                "isMultiplication": False,
                "hReferenceCount": 0,
                "isBaseMaterial": filename == self.BASE_MATERIAL_FILE,
                "isProduct": False,
                "productID": None,
                "references": [],
                "error": error_msg
            }
        
        # Add product mapping immediately
        product_id = self.product_mapper.reverse_mapping.get(obj_id)
        
        result = {
            "id": obj_id,
            "file": filename,
            "sheet": sheet_name,
            "cell": cell_ref,
            "formula": None,
            "cleaned_formula": None,
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
            wb = ExcelUtils.get_workbook(file_path)
            
            # Access specific sheet directly instead of loading all
            if sheet_name not in wb.sheetnames:
                raise ValueError(f"Sheet {sheet_name} not found")
            
            ws = wb[sheet_name]  # Direct sheet access
            cell = ws[cell_ref]
            
            formula, value = self.excel_helper.get_cell_info(file_path, sheet_name, cell_ref)
            result['formula'] = formula
            result['value'] = value

            # Clean the formula before storing and parsing
            cleaned_formula = self.cleaner.clean_formula(formula)
            result['cleaned_formula'] = cleaned_formula
            
            if cleaned_formula:
                formula_info = self.parser.parse_formula(cleaned_formula, filename, sheet_name)
                result.update(formula_info)
                # Check for multiplication
                result['isMultiplication'] = '*' in cleaned_formula
                if result['isMultiplication']:
                    self.logger.warning(f"Multiplication found in {filename} {sheet_name}!{cell_ref}")

                result = self.resolver.resolve_references(result, max_depth=self.max_recursion_depth)
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error processing {filename} {sheet_name}!{cell_ref}: {error_msg}")
            result['error'] = error_msg
        
        return result

