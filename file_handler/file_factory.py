import json
import os
from datetime import datetime
from typing import Dict, Any
from .file_context import FileContext
from logger import get_logger


class FileFactory:
    """
    Handles creation and management of snapshot files and snapshot ID records.

    This class provides methods to save snapshots as JSON files and maintain
    a record of snapshot IDs with timestamps. It uses a FileContext for safe
    file operations and includes logging via decorators.

    Attributes:
        base_output_dir (str): Base directory for all output files.
        snapshots_dir (str): Directory for storing snapshot files.
        snapshot_ids_dir (str): Directory for storing snapshot ID records.
        file_context (FileContext): Context manager for safe file operations.

    Methods:
        save_snapshot(data: Dict[str, Any], name: str) -> str:
            Saves a snapshot to a JSON file.
        save_snapshot_id(snapshot_id: str) -> str:
            Saves a snapshot ID with a timestamp to a JSON file.
        save_snapshot_list(platform: str, data: Dict[str, Any]) -> str:
            Saves the snapshot list to a JSON file named after the platform.

    Raises:
        None: This class handles exceptions internally through FileContext.

    Example:
        >>> factory = FileFactory()
        >>> snapshot = {"data": [1, 2, 3]}
        >>> file_path = factory.save_snapshot(snapshot, "example_snapshot")
        >>> print(file_path)
        '/path/to/output/snapshots/example_snapshot.json'
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

    def save_snapshot(self, data: Dict[str, Any], name: str) -> str:
        """Save snapshot to a JSON file with a given name and unique ID."""
        filename = f"{name}.json"
        filepath = os.path.join(self.snapshots_dir, filename)

        with self.file_context.safe_open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        log.info(f"Snapshot saved successfully: {filename} at {filepath}")
        return filepath

    def save_snapshot_id(self, snapshot_id: str) -> str:
        """Save snapshot ID with timestamp."""
        filename = "snapshots.json"
        filepath = os.path.join(self.snapshot_ids_dir, filename)

        existing_data = []
        if os.path.exists(filepath):
            with self.file_context.safe_open(filepath, "r") as f:
                existing_data = json.load(f)

        new_entry = {
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
        }
        existing_data.append(new_entry)

        with self.file_context.safe_open(filepath, "w") as f:
            json.dump(existing_data, f, indent=4)

        log.info(f"Snapshot ID saved successfully: {filename} at {filepath}")
        return filepath

    def save_snapshot_list(self, platform: str, data: Dict[str, Any]) -> str:
        """Save the snapshot list to a JSON file named after the platform."""
        filename = f"{platform}_list.json"
        filepath = os.path.join(self.base_output_dir, "outputs", filename)

        # Ensure the outputs directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with self.file_context.safe_open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        log.info(f"Snapshot list saved successfully: {filename} at {filepath}")
        return filepath
    