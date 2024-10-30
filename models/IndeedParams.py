from dataclasses import dataclass, field
from typing import Optional, Dict
from logger import get_logger

dataset_id = "gd_l4dx9j9sscpvs7no2"
platform_name = "Indeed"

@dataclass(frozen=True)
class IndeedParams:
    """
    A class to represent Indeed job search parameters.

    Attributes:
        location (Optional[str]): The location to search for jobs.
        keywords (Optional[str]): The keywords to use in the job search.
        country (str): The country code for the job search (default is "PH").
        domain (str): The domain for the job search (default is "ph.indeed.com").
    """
    location: Optional[str] = ""
    keywords: Optional[str] = ""
    country: str = field(default="PH", init=False)
    domain: str = field(default="ph.indeed.com", init=False)

    def __post_init__(self):
        """
        Validate the types and values of fields after initialization.
        """
        log = get_logger("Indeed params")

        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            
    def to_dict(self) -> Dict:
        """
        Convert the IndeedParams object to a dictionary.

        Returns:
            Dict: A dictionary representation of the IndeedParams object.
        """
        result = {
            "country": self.country,
            "domain": self.domain,
            "location": self.location,
            "keyword_search": self.keywords,
        }

        return result

    def get_dataset_id(self):
        """
        Retrieve the BrightData dataset ID.

        Returns:
            str: The unique identifier for the BrightData dataset.
        """
        return dataset_id
    
    def get_platform_name(self):
        """
        Retrieve the platform

        Returns:
            str: The platform name.
        """
        return platform_name
    
    def __dict__(self):
        return self.to_dict()
