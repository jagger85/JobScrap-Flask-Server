from typing import Dict, Any
from .file_factory import FileFactory
from logger import file_logger as log


class FileManager:
    """
    Manages file operations for snapshots and snapshot IDs.

    This class provides methods to process and save snapshots and snapshot IDs
    using a FileFactory instance. It includes error handling and logging for
    file operations.

    Attributes:
        file_factory (FileFactory): An instance of FileFactory used for file operations.

    Methods:
        process_and_save_snapshot(snapshot: Dict[str, Any], snapshot_id: str) -> str:
            Processes and saves a snapshot in a single operation.
        process_snapshot_id(snapshot_id: str) -> str:
            Processes and saves a snapshot ID.
        process_snapshot(snapshot: Dict[str, Any], snapshot_id: str) -> str:
            Processes and saves a snapshot.

    Raises:
        Exception: Re-raises any exceptions caught during file operations.

    Example:
        >>> file_manager = FileManager()
        >>> snapshot = {"data": [1, 2, 3]}
        >>> file_path = file_manager.process_and_save_snapshot(snapshot, "example_snapshot")
        >>> print(file_path)
        '/path/to/saved/snapshot.json'
    """

    def __init__(self):
        self.file_factory = FileFactory()

    def process_and_save_snapshot(
        self, snapshot: Dict[str, Any], snapshot_id: str
    ) -> str:
        """
        Process and save a snapshot in a single operation.

        Args:
            snapshot (Dict[str, Any]): The snapshot data to process.
            snapshot_id (str): The ID of the snapshot.
        """
        try:
            # Process snapshot ID and data in one go
            self.process_snapshot_id(snapshot_id)
            self.process_snapshot(snapshot, snapshot_id)
        except Exception as e:
            log.error(f"Error processing and saving snapshot: {str(e)}")
            raise

    def process_snapshot_id(self, snapshot_id: str) -> str:
        """
        Process and save the snapshot ID.

        Args:
            snapshot_id (str): The snapshot ID to track

        Returns:
            str: Path to the saved snapshot ID file
        """
        try:
            snapshot_path = self.file_factory.save_snapshot_id(snapshot_id)
            return snapshot_path
        except Exception as e:
            log.error(f"Error processing snapshot ID: {str(e)}")
            raise

    def process_snapshot(self, snapshot: Dict[str, Any], snapshot_id: str) -> str:
        """
        Process and save the snapshot.

        Args:
            snapshot (Dict[str, Any]): The snapshot to save
            snapshot_id (str): The ID of the snapshot

        Returns:
            str: Path to the saved snapshot file
        """
        try:
            snapshot_path = self.file_factory.save_snapshot(snapshot, snapshot_id)
            return snapshot_path
        except Exception as e:
            log.error(f"Error processing snapshot: {str(e)}")
            raise
