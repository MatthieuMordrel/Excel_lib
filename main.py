from pathlib import Path
from batch_processor import BatchRequest, get_batch_requests
from Mappings.product_mapper import ProductMapper
from result_manager import ResultManager
from utils.logging_utils import setup_logger
from file_indexer import FileIndexer
from cell_info_extractor import CellInfoExtractor
from typing import List

# Configuration
USE_BATCH_FILE = True
BATCH_FILE_PATH = Path(__file__).parent / "Batch File" / "File - Tab - Cell - (start of recursive resolver) - New.xlsx"
BASE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\BASISMATERIALEN")
LOG_PATH = Path("Logs/log.json")
PRODUCT_MAPPING_PATH = Path("Mappings/product_mapping.json")

def get_test_batch() -> List[BatchRequest]:
    """Returns a predefined test batch of requests."""
    return [
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"), #Simple Multiplication =+C19*D17
        # ("2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx", "OVERZICHT COZ1323", "G33"), #Multiplication & external reference to base material
        # ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"), #3 external references
        # ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "G17"), #SUM + 2 internal references
        # ("2022 - P6 berekening kolomkast 2137.xlsx", "DE446x2137", "H39"), #Element
        # ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "E17"), #Sum of 2 elements
        # ("2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx", "LADE 30", "R36"), #Division
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D35"), #Element + External reference
        # ("2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx", "PLADE 30", "W18"), #Element + Base material reference
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "B28"), #Element + Division weird stuff
        # # ("2022 - P5 berekening kolomkast 2317.xlsx", "OVERZICHT CK231", "D17"), #Product Kost
        # # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D35"), #Error

         #Products Cost
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D17"), #Elements
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D35"), #Elements + Local Products
        # ("2022 -P1 Berekening Kolom P Lade B Lade(16-10) 2137-KLEUR.xlsx", "OVERZICHT CKP222", "D22"), #Local Products + External products
        # ("2022 -P1 Berekening Kolom P Lade B Lade(16-10) 2137-KLEUR.xlsx", "OVERZICHT CKP222", "D3"), #Elements + External Products
        # ("2022 -P1 Berekening Kolom P Lade F+O (11-12-14-17-18-19-20-21-23) 2137-KLEUR.xlsx", "OVERZICHT CKP222", "G3"), #Local products
        # # ("2022 -P4 Berekening  Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "D11"), #Elements + Hardcoded
        # # ("2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "M35"), #Local Products + ALU BODEM - Hardcoded value
        # ("2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "D65"), #Elements + Multiplied Elements
        # ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"), #External Products
        # # ("2022 -P1 Berekening FLES-LFR - PL 794-KLEUR.xlsx", "OVERZICHT PO", "G3"), #Mistake

        #product Prices
        # ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"),
        # ("2022 - P2 Berekening Open Kolomkast 2227-KLEUR.xlsx", "OVERZICHT COK222", "D5"),
        # ("2022 -P2 Berekening Kolom F+O (13-22-24-31-32-33-35-37+38+39) 2227-KLEUR.xlsx", "OVERZICHT CK222", "H3"),
        ("2022 - P1 Berekening klapdeurHangkast 494-565 KLEUR.xlsx", "OVERZICHT C494", "D5"), #Standard + Material
        ("2022 - P1 Berekening GLAS DEUR Hangkast 970-KLEUR.xlsx", "OVERZICHT C79B", "D41"), #Standard + Hardocded
        # ("2022 - P1 Berekening GLAS DEUR Hangkast 970-KLEUR.xlsx", "OVERZICHT C79B", "D33"),
        # ("2022 - P1 Berekening Hoekonderkasten 794-KLEUR.xlsx", "OVERZICHT CO", "F5"),


    ]


def main():
    # Initialize components
    setup_logger(Path("Logs/excel_processor.log"))
    product_mapper = ProductMapper(PRODUCT_MAPPING_PATH)
    result_manager = ResultManager(LOG_PATH)
    
    # Load product mapping
    product_mapper.load_mapping()
    
    # Get batch requests
    batch_requests = get_batch_requests(BATCH_FILE_PATH) if USE_BATCH_FILE else get_test_batch()
    
    # Log total number of products to process
    total_products = len(batch_requests)
    print(f"\nStarting processing of {total_products} products...")
    
    # Create file index
    indexer = FileIndexer(BASE_PATH)
    file_index = indexer.create_file_index()
    
    # Control parameter for recursion on multiplication
    STOP_ON_MULTIPLICATION = False  # Set this to False if you don't want to stop on multiplication
    STOP_ON_DIVISION = False
    
    # Process results directly with CellInfoExtractor
    extractor = CellInfoExtractor(file_index, product_mapper, max_recursion_depth=10, stop_on_multiplication=STOP_ON_MULTIPLICATION, stop_on_division=STOP_ON_DIVISION)
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