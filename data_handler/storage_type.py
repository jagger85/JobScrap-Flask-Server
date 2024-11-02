from enum import Enum


class StorageType(Enum):
    """
    Enum defining supported storage types for the application.
    This allows for type-safe storage selection and easy extension
    by adding new storage types.

    Available storage types:
        FILE: For file-based storage (JSON files)
        DATABASE: For database storage
        CSV: For csv-based storage (CSV files)
    """

    JSON = "file"
    DATABASE = "database"
    CSV = "csv"
