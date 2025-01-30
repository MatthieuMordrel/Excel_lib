from pathlib import Path
from batch_processor import get_batch_requests
from Mappings.product_mapper import ProductMapper
from result_manager import ResultManager
from utils.logging_utils import setup_logger
from file_indexer import FileIndexer
from cell_info_extractor import CellInfoExtractor

# Configuration
USE_BATCH_FILE = False
BATCH_FILE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files\Batch File\File - Tab - Cell - (start of recursive resolver) - New.xlsx")
BASE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\BASISMATERIALEN")
LOG_PATH = Path("Logs/log.json")
PRODUCT_MAPPING_PATH = Path("Mappings/product_mapping.json")

def get_test_batch() -> list:
    """Returns a predefined test batch of requests."""
    return [
        ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"), #Simple Multiplication =+C19*D17
        ("2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx", "OVERZICHT COZ1323", "G33"), #Multiplication & external reference to base material
        ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"), #3 external references
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "G17"), #SUM + 2 internal references
        ("2022 - P6 berekening kolomkast 2137.xlsx", "DE446x2137", "H39"), #Element
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "E17"), #Sum of 2 elements
        ("2022 -P7 Berekening Kolom P Lade F+O (11-12-14-17-18-19-20-21-23) 2137-KLEUR.xlsx", "OVERZICHT CKP213", "I3") #Internal reference with space
    ]

def main():
    # Initialize components
    logger = setup_logger(Path("Logs/excel_processor.log"))
    product_mapper = ProductMapper(PRODUCT_MAPPING_PATH)
    result_manager = ResultManager(LOG_PATH)
    
    # Load product mapping
    product_mapper.load_mapping()
    
    # Get batch requests
    batch_requests = get_batch_requests(BATCH_FILE_PATH) if USE_BATCH_FILE else get_test_batch()
    
    # Create file index
    indexer = FileIndexer(BASE_PATH)
    file_index = indexer.create_file_index() # type: Dict[str, Path]
    
    # Control parameter for recursion on multiplication
    stop_on_multiplication = False  # Set this to False if you don't want to stop on multiplication
    
    # Process results directly with CellInfoExtractor
    extractor = CellInfoExtractor(file_index, product_mapper, max_recursion_depth=10, stop_on_multiplication=stop_on_multiplication)
    results = extractor.extract_batch(batch_requests)
    
    # Save results and log summary
    result_manager.save_results(results)
    
    # Print summary to console
    print("\nFinal Classification Summary:")
    print(f"Products: {result_manager.summary_logger.counts['products']}")
    print(f"Elements: {result_manager.summary_logger.counts['elements']}")
    print(f"Base Materials: {result_manager.summary_logger.counts['base_materials']}")
    print(f"Other/Intermediate: {result_manager.summary_logger.counts['other']}")

if __name__ == "__main__":
    main() 