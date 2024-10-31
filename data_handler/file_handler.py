import json
import os
from typing import Dict, Any, Union
from .file_context import FileContext
from logger import get_logger
from data_handler.base_data_handler import BaseDataHandler


class FileHandler(BaseDataHandler):
    """
    Handles data storage operations using the file system.
    
    This class implements the BaseDataHandler interface to provide
    file-based storage operations. It manages JSON file creation,
    updates, and retrieval while handling all file system interactions.

    Attributes:
        base_output_dir (str): Base directory for all output files
        snapshots_dir (str): Directory for storing snapshot files
        snapshot_ids_dir (str): Directory for storing snapshot ID records
        file_context (FileContext): Context manager for safe file operations
    """

    def __init__(self, base_output_dir: str = "output"):
        global log
        log = get_logger("File handler")
        self.base_output_dir = base_output_dir
        self.snapshots_dir = os.path.join(base_output_dir, "snapshots")
        self.snapshot_ids_dir = os.path.join(base_output_dir, "snapshots-id")
        self.file_context = FileContext()

        # Ensure directories exist
        for directory in [self.snapshots_dir, self.snapshot_ids_dir]:
            os.makedirs(directory, exist_ok=True)

    def store_snapshot(self, data: Dict[str, Any], name: str) -> str:
        """Save snapshot to a JSON file with a given name and unique ID."""
        filename = f"{name}.json"
        filepath = os.path.join(self.snapshots_dir, filename)

        with self.file_context.safe_open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        log.info(f"Snapshot saved successfully: {filename} at {filepath}")
        return filepath


    def store_snapshot_list(self, dataset_id: str, snapshot_list: Union[dict, list]) -> str:
        """Save the snapshot list to a JSON file named after the dataset_id."""
        filename = f"{dataset_id}_list.json"
        filepath = os.path.join(self.base_output_dir, "outputs", filename)

        # Ensure the outputs directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with self.file_context.safe_open(filepath, "w") as f:
            json.dump(snapshot_list, f, indent=4)

        log.info(f"Snapshot list saved successfully: {filename} at {filepath}")
        return filepath

    def get_snapshot(self):
        log.warning("Method not implemented yet")
        pass
    
    def get_snapshot_list(self):
        log.warning("Method not implemented yet")
        pass