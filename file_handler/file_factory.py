import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any
from .file_context import FileContext
from .file_decorators import log_file_operation

class FileFactory:
    """
    Handles creation and management of dataset files and dataset ID records.

    This class provides methods to save datasets as JSON files and maintain
    a record of dataset IDs with timestamps. It uses a FileContext for safe
    file operations and includes logging via decorators.

    Attributes:
        base_output_dir (str): Base directory for all output files.
        datasets_dir (str): Directory for storing dataset files.
        dataset_ids_dir (str): Directory for storing dataset ID records.
        file_context (FileContext): Context manager for safe file operations.

    Methods:
        save_dataset(data: Dict[str, Any], name: str) -> str:
            Saves a dataset to a JSON file.
        save_dataset_id(dataset_id: str) -> str:
            Saves a dataset ID with a timestamp to a JSON file.

    Raises:
        None: This class handles exceptions internally through FileContext.

    Example:
        >>> factory = FileFactory()
        >>> dataset = {"data": [1, 2, 3]}
        >>> file_path = factory.save_dataset(dataset, "example_dataset")
        >>> print(file_path)
        '/path/to/output/datasets/example_dataset.json'
    """

    def __init__(self, base_output_dir: str = "output"):
        self.base_output_dir = base_output_dir
        self.datasets_dir = os.path.join(base_output_dir, "datasets")
        self.dataset_ids_dir = os.path.join(base_output_dir, "datasets-id")
        self.file_context = FileContext()
        
        # Ensure directories exist
        for directory in [self.datasets_dir, self.dataset_ids_dir]:
            os.makedirs(directory, exist_ok=True)

    @log_file_operation
    def save_dataset(self, data: Dict[str, Any], name: str) -> str:
        """Save dataset to a JSON file with a given name and unique ID."""
        filename = f"{name}.json"
        filepath = os.path.join(self.datasets_dir, filename)
        
        with self.file_context.safe_open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return filepath

    @log_file_operation
    def save_dataset_id(self, dataset_id: str) -> str:
        """Save dataset ID with timestamp."""
        filename = f"datasets.json"
        filepath = os.path.join(self.dataset_ids_dir, filename)
        
        existing_data = []
        if os.path.exists(filepath):
            with self.file_context.safe_open(filepath, 'r') as f:
                existing_data = json.load(f)
        
        new_entry = {
            "dataset_id": dataset_id,
            "timestamp": datetime.now().isoformat(),
        }
        existing_data.append(new_entry)
        
        with self.file_context.safe_open(filepath, 'w') as f:
            json.dump(existing_data, f, indent=4)
        return filepath
