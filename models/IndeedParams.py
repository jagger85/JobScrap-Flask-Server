from dataclasses import dataclass, field
from typing import Dict
from logger.logger import get_logger
from enum import Enum
from constants.date_range import DateRange
dataset_id = "gd_l4dx9j9sscpvs7no2"
platform_name = "Indeed"

class TimeRange(Enum):
    PAST_24_HOURS = "Last 24 hours"
    PAST_3_DAYS = "Last 3 days"
    PAST_7D_DAYS = "Last 7 days"
    PAST_14_DAYS = "Last 14 days"

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
    #TODO add location
    location: str = None
    keywords: str = field(default="software developer", init=False)
    country: str = field(default="PH", init=False)
    domain: str = field(default="ph.indeed.com", init=False)
    time_range = DateRange

    def __post_init__(self):
        """
        Validate the types and values of fields after initialization.
        """
        log = get_logger("Indeed")

        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")
            raise

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            raise

        if self.time_range == DateRange.PAST_24_HOURS:
            self.time_range == TimeRange.PAST_24_HOURS
        
        elif self.time_range == DateRange.PAST_WEEK:
            self.time_range == TimeRange.PAST_7_DAYS
        
        elif self.time_range == DateRange.PAST_15_DAYS:
            self.time_range == TimeRange.PAST_14_DAYS
        
        elif self.time_range == DateRange.PAST_MONTH:
            log.warning("Indeed does not provide a last month search looking for las 14 days instead")
            self.time_range == TimeRange.PAST_14_DAYS
        
            
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
            "date_posted": self.time_range.value
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
