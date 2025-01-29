from pathlib import Path
from batch_processor import get_batch_requests, process_batch
from product_mapper import ProductMapper
from result_manager import ResultManager
from utils.logging_utils import setup_logger, log_request_completion, log_summary

# Configuration
USE_BATCH_FILE = False
BATCH_FILE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files\Batch File\File - Tab - Cell - (start of recursive resolver) - New.xlsx")
BASE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\BASISMATERIALEN")
LOG_PATH = Path("log.json")
PRODUCT_MAPPING_PATH = Path("product_mapping.json")

def get_test_batch() -> list:
    """Returns a predefined test batch of requests."""
    return [
        ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"),
        ("2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx", "OVERZICHT COZ1323", "G33"),
        ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "G17"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "DE446x2137", "H39"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "E17"),
        ("2022 - P2 Berekening opzetkast 1413-KLEUR met lade.xlsx", "OVERZICHT COZ1323", "E33"),
        ("2022 -P7 Berekening Kolom P Lade F+O (11-12-14-17-18-19-20-21-23) 2137-KLEUR.xlsx", "OVERZICHT CKP213", "I3")
    ]

def main():
    # Initialize components
    logger = setup_logger()
    product_mapper = ProductMapper(PRODUCT_MAPPING_PATH)
    result_manager = ResultManager(LOG_PATH)
    
    # Load product mapping
    product_mapper.load_mapping()
    
    # Get batch requests
    batch_requests = get_batch_requests(BATCH_FILE_PATH) if USE_BATCH_FILE else get_test_batch()
    
    # Process results
    results = process_batch(batch_requests, BASE_PATH)
    
    # Enrich results with product information
    results = product_mapper.enrich_results(results)
    
    # Save results
    result_manager.save_results(results)
    
    # Log completion of each request
    for result in results:
        log_request_completion(logger, result)
    
    # Print summary
    log_summary(logger, LOG_PATH)

if __name__ == "__main__":
    main() 