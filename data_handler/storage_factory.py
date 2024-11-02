from data_handler.storage_type import StorageType
from data_handler.base_data_handler import BaseDataHandler
from data_handler.database_handler import DatabaseHandler
from data_handler.json_handler import FileHandler
from data_handler.csv_handler import CsvHandler


class StorageFactory:
    """
    Factory class implementing the Factory Pattern for creating storage handlers.

    This class provides a centralized way to create storage handler instances
    based on the specified storage type. It decouples the storage handler creation
    from the rest of the application, making it easier to add new storage types.

    Usage:
        storage_type = StorageType.FILE
        handler = StorageFactory.get_storage_handler(storage_type)
    """

    @staticmethod
    def get_storage_handler(storage_type: StorageType) -> BaseDataHandler:
        """
        Creates and returns appropriate storage handler based on storage type.

        Args:
            storage_type (StorageType): The type of storage handler to create

        Returns:
            BaseDataHandler: An instance of the appropriate storage handler

        Raises:
            ValueError: If an unsupported storage type is provided
        """
        if storage_type == StorageType.JSON:
            return FileHandler()
        elif storage_type == StorageType.DATABASE:
            return DatabaseHandler()
        elif storage_type == StorageType.CSV:
            return CsvHandler()
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
