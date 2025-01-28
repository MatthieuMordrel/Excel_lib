import os
from pathlib import Path
from file_indexer import FileIndexer
from cell_info_extractor import CellInfoExtractor
from utils.excel_utils import save_to_log

def main():
    # Initialize file indexer
    base_path = r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\BASISMATERIALEN"
    #Return Dict[str, Path]: Dictionary mapping filenames to their full paths
    #Ex: {'2022 - P1 berekening kolomkast 2137.xlsx': PosixPath('C:/Users/matth/OneDrive - Matthieu Mordrel/Work/Projects/Kovera/Project 2/BASISMATERIALEN/6 -2022- COMFORTLINE - VLAK LAK  + CORPUS KLEUR/2022 - P6 berekening kolomkast 2137.xlsx')}
    indexer = FileIndexer(Path(base_path))
    file_index = indexer.create_file_index()
    
    # Initialize cell info extractor
    extractor = CellInfoExtractor(file_index)
    
    # Example batch of cells to process
    batch_requests = [
        ("2022 - P1 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "D19"),
        ("2022 - P1 Berekening opzetkast 1323-KLEUR.xlsx", "OVERZICHT COZ1323", "G33"),
        ("2022 -P2 Berekening 2b Ladenkasten 794-KLEUR.xlsx", "OVERZICHT COP", "F65"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "G17"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "DE446x2137", "H39"),
        ("2022 - P6 berekening kolomkast 2137.xlsx", "OVERZICHT CK213", "E17")
    ]
    
    # Process the batch
    results = extractor.extract_batch(batch_requests)
    
    # Save results to log
    log_path = os.path.join(os.getcwd(), "log.json")
    for result in results:
        save_to_log(result, log_path)
        print(result)

if __name__ == "__main__":
    main() 