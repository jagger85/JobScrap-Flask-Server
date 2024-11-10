from dataclasses import dataclass, field
from typing import Dict
from logger.logger import get_logger
from constants.date_range import DateRange

dataset_id = "gd_l4dx9j9sscpvs7no2"
platform_name = "Indeed"

@dataclass(frozen=True)
class IndeedParams:
    """
    A class to represent Indeed job search parameters.
    """
    location: str = field(default="philippines", init=False)
    keywords: str = field(default="software developer", init=False)
    country: str = field(default="PH", init=False)
    domain: str = field(default="ph.indeed.com", init=False)
    date_range: DateRange
    _time_range: str = field(init=False)

    def __post_init__(self):
        """
        Convert DateRange to Indeed-specific time range string and validate fields.
        """
        log = get_logger("Indeed")
        
        # Create a dict object to store the frozen dataclass attributes
        object.__setattr__(self, '_time_range', self._convert_date_range(self.date_range))

        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")
            raise ValueError("Location must be a non-empty string")

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            raise ValueError("Keywords must be a non-empty string")

    @staticmethod
    def _convert_date_range(date_range: DateRange) -> str:
        """Convert DateRange enum to Indeed-specific string format."""
        date_range_mapping = {
            DateRange.PAST_24_HOURS: 'Last 24 hours',
            DateRange.PAST_WEEK: 'Last 7 days',
            DateRange.PAST_15_DAYS: 'Last 14 days',
            DateRange.PAST_MONTH: 'Last 14 days',  # Adapted for Indeed's limitations
        }
        return date_range_mapping.get(date_range, 'Unknown')

    def to_dict(self) -> Dict:
        """Convert the IndeedParams object to a dictionary."""
        return {
            "country": self.country,
            "domain": self.domain,
            "location": self.location,
            "keyword_search": self.keywords,
            "date_posted": self._time_range
        }

    def get_dataset_id(self):
        """
        Retrieve the BrightData dataset ID.

        Returns:
            str: The unique identifier for the BrightData dataset.
        """
        return dataset_id
    
    def get_platform_name(self):
        """
        Retrieve the platform name.

        Returns:
            str: The platform name.
        """
        return platform_name
    
    def __dict__(self):
        return self.to_dict()
