from pathlib import Path
from batch_processor import get_batch_requests, process_batch
from cell_info_extractor import CellInfoExtractor
from file_indexer import FileIndexer
import json

# Configuration - Set this to True to use batch file, False for test data
USE_BATCH_FILE = False
BATCH_FILE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files\Batch File\File - Tab - Cell - (start of recursive resolver).xlsx")
BASE_PATH = Path(r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\BASISMATERIALEN")
LOG_PATH = Path("log.json")

def get_test_batch() -> list:
    """Returns a predefined test batch of requests."""
    return [
        ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"),
        ("2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx", "OVERZICHT COZ1323", "G33"),
        ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "G17"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "DE446x2137", "H39"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "E17"),
        ("2022 - P2 Berekening opzetkast 1413-KLEUR met lade.xlsx", "OVERZICHT COZ1323", "E33")

    ]

def main():
    # Get batch requests
    if USE_BATCH_FILE:
        print("Processing from batch file...")
        batch_requests = get_batch_requests(BATCH_FILE_PATH)
    else:
        print("Processing test batch...")
        batch_requests = get_test_batch()
    
    # Process and save results
    results = process_batch(batch_requests, BASE_PATH)
    for result in results:
        with open(LOG_PATH, 'a') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
        print(result)

if __name__ == "__main__":
    main() 