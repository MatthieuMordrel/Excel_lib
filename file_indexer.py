from pathlib import Path
from typing import Dict
import os

FileIndex = Dict[str, Path]

class FileIndexer:
    """Handles indexing of Excel files in a directory structure."""
    
    def __init__(self, base_folder: Path):
        self.base_folder = base_folder
    
    def create_file_index(self) -> FileIndex:
        """
        Create an index of all Excel files in the base folder.
        
        Returns:
            Dict[str, Path]: Dictionary mapping filenames to their full paths
        """
        file_index: FileIndex = {}
        for root, _, files in os.walk(self.base_folder):
            for file in files:
                if file.endswith(('.xlsx', '.xls', '.xlsm')):
                    file_index[file] = Path(root) / file
        return file_index 