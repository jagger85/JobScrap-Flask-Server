from abc import ABC, abstractmethod
import json
from models.JobListing import JobListing

class BaseDataHandler(ABC):
    """
    Abstract base class defining the interface for all storage handlers.
    
    This class serves as a contract that all storage implementations must follow,
    ensuring consistent behavior across different storage types. It follows the
    Strategy Pattern, allowing different storage implementations to be used
    interchangeably.

    To implement a new storage type:
    1. Create a new class that inherits from BaseDataHandler
    2. Implement all abstract methods
    3. Add the new storage type to StorageType enum
    4. Update StorageFactory to handle the new type
    """

    def __init__(self):
        pass

    @abstractmethod
    def store_snapshot(self, job_listings: list[JobListing]):
        """Store a snapshot data in the storage system."""
        pass
    
    @abstractmethod
    def store_snapshot_list(self, dataset_id: str, snapshot_list: json):
        """Store a snapshot list based on a dataset id."""
        pass

    @abstractmethod
    def get_snapshot(self):
        """Retrieve a snapshot from storage."""
        pass
    
    @abstractmethod
    def get_snapshot_list(self):
        """Retrieve a list of available snapshots."""
        pass
    
    @abstractmethod
    def return_snapshot(self,job_listings: list[JobListing]):
        """Return a snapshot"""
        pass