from typing import Dict, Any, Optional
from .file_factory import FileFactory
from .file_decorators import log_file_operation
from logger import file_handler

class FileManager:
    """
    Manages file operations for datasets and snapshot IDs.

    This class provides methods to process and save datasets and snapshot IDs
    using a FileFactory instance. It includes error handling and logging for
    file operations.

    Attributes:
        file_factory (FileFactory): An instance of FileFactory used for file operations.

    Methods:
        process_dataset(dataset: Dict[str, Any], dataset_name: str) -> str:
            Processes and saves a dataset.
        process_dataset_id(snapshot_id: str) -> str:
            Processes and saves a snapshot ID.

    Raises:
        Exception: Re-raises any exceptions caught during file operations.

    Example:
        >>> file_manager = FileManager()
        >>> dataset = {"data": [1, 2, 3]}
        >>> file_path = file_manager.process_dataset(dataset, "example_dataset")
        >>> print(file_path)
        '/path/to/saved/dataset.json'
    """

    def __init__(self):
        self.file_factory = FileFactory()

    @log_file_operation
    def process_dataset(self, dataset: Dict[str, Any], dataset_name: str) -> str:
        """
        Process and save the dataset.
        
        Args:
            dataset (Dict[str, Any]): The dataset to save
            dataset_name (str): The name to use for the dataset file
            
        Returns:
            str: Path to the saved dataset file
        """
        try:
            dataset_path = self.file_factory.save_dataset(dataset, dataset_name)
            return dataset_path
        except Exception as e:
            file_handler.error(f"Error processing dataset: {str(e)}")
            raise

    @log_file_operation
    def process_dataset_id(self, snapshot_id: str) -> str:
        """
        Process and save the snapshot ID.
        
        Args:
            snapshot_id (str): The snapshot ID to track
            
        Returns:
            str: Path to the saved snapshot ID file
        """
        try:
            snapshot_path = self.file_factory.save_dataset_id(snapshot_id)
            return snapshot_path
        except Exception as e:
            file_handler.error(f"Error processing snapshot ID: {str(e)}")
            raise
