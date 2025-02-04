from typing import Dict, List, Tuple
from pathlib import Path
from utils.excel_utils import ExcelHelper, ExcelUtils
from utils.formula_parser import FormulaParser
from utils.formula_cleaner import FormulaCleaner
from utils.logging_utils import setup_logger
from utils.recursive_resolver import RecursiveResolver
from Mappings.product_mapper import ProductMapper
from schema.schema import FormulaResult, FormulaInfo
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet



class CellInfoExtractor:
    """Handles extraction of cell information from Excel files."""
    
    def __init__(self, file_index: Dict[str, Path], product_mapper: ProductMapper, max_recursion_depth: int = 10, stop_on_multiplication: bool = True):
        self.file_index = file_index
        self.max_recursion_depth = max_recursion_depth
        self.excel_helper = ExcelHelper()
        self.parser = FormulaParser()
        self.cleaner = FormulaCleaner()
        self.logger = setup_logger()
        self.resolver = RecursiveResolver(self, self.logger, stop_on_multiplication)
        self.BASE_MATERIAL_FILE = "calculatie cat 2022 .xlsx".replace(" ", "")
        self.product_mapper = product_mapper
        self.stop_on_multiplication = stop_on_multiplication
        
        # Add counters
        self.total_formulas = 0
        self.multiplication_count = 0
        self.division_count = 0
        self.processed_products = 0  # New counter for progress tracking

    def extract_batch(self, requests: List[Tuple[str, str, str]]) -> List[FormulaResult]:
        """Processes a batch of cell extraction requests."""
        results: List[FormulaResult] = []
        total_products = len(requests)
        
        for i, (file_name, sheet_name, cell_ref) in enumerate(requests, 1):
            result = self.extract_cell_info(file_name, sheet_name, cell_ref)
            results.append(result)
            
            # Log progress every 10 products
            if i % 10 == 0 or i == total_products:
                print(f"Processed {i}/{total_products} products...")
                
        return results

    def extract_cell_info(self, filename: str, sheet_name: str, cell_ref: str) -> FormulaResult:
        """Extracts formula and value from a specific cell."""
        # Create unique ID for the cell
        id = f"{filename}_{sheet_name}_{cell_ref}".replace(" ", "")
        self.logger.debug(f"Extracting cell info: {id}")
        obj_id = id
        
        file_path = self.file_index.get(filename)
        if not file_path:
            error_msg = f"File {filename} not found in index"
            self.logger.error(error_msg)
            return FormulaResult({
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
                "isDivision": False,
                "hReferenceCount": 0,
                "isBaseMaterial": filename.replace(" ", "") == self.BASE_MATERIAL_FILE,
                "isProduct": False,
                "productID": None,
                "error": error_msg,
                "references": [],
            })
        
        # Add product mapping immediately
        product_id: str | None = self.product_mapper.reverse_mapping.get(obj_id)
        isProduct: bool = product_id is not None

        result: FormulaResult = {
            "id": obj_id,
            "file": filename,
            "sheet": sheet_name,
            "cell": cell_ref,
            "formula": None,
            "cleaned_formula": None,
            "value": None,
            "path": str(file_path),
            "isProduct": isProduct,
            "productID": product_id,
            "isElement": False,
            "isBaseMaterial": filename == self.BASE_MATERIAL_FILE,
            "isMultiplication": False,
            "isDivision": False,
            "hReferenceCount": 0,
            "error": None,
            "references": [],
        }
        
        try:
            wb: Workbook = ExcelUtils.get_workbook(file_path)
            if sheet_name not in wb.sheetnames:
                raise ValueError(f"Sheet {sheet_name} not found")
            ws: Worksheet = wb[sheet_name]
            _ = ws[cell_ref]  # Verify cell exists
            
            formula, value = self.excel_helper.get_cell_info(file_path, sheet_name, cell_ref)
            result['formula'] = formula
            result['value'] = value

            # Clean the formula before storing and parsing
            cleaned_formula = self.cleaner.clean_formula(formula)
            result['cleaned_formula'] = cleaned_formula

            if cleaned_formula:
                self.total_formulas += 1  # Increment total formulas counter
                # Check for multiplication and division
                result['isMultiplication'] = '*' in cleaned_formula
                result['isDivision'] = '/' in cleaned_formula
                if self.stop_on_multiplication and result['isMultiplication']:
                    self.logger.warning(f"Multiplication found in: {result['id']}")
                    return result
                if result['isDivision']:
                    self.logger.warning(f"Division found in: {result['id']}")
                    return result
            
                formula_info: FormulaInfo = self.parser.parse_formula(cleaned_formula, filename, sheet_name)
                result['hReferenceCount'] = formula_info['hReferenceCount']
                result['isElement'] = formula_info['isElement']

                if not result['isElement']:  # Only resolve references if it's not an element
                    result['references'] = formula_info['references']
                    result = self.resolver.resolve_references(result, max_depth=self.max_recursion_depth)

        except FileNotFoundError as e:
            self.logger.error(f"File not found: {file_path}")
            result['error'] = "File not found"
            return result
        except KeyError as e:
            self.logger.error(f"Cell or sheet not found: {str(e)}")
            result['error'] = "Cell or sheet not found"
            return result
        
        return result

