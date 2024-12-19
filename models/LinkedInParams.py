from dataclasses import dataclass, field
from typing import Dict
from enum import Enum
from constants.date_range import DateRange
from logger.logger import get_logger

dataset_id = "gd_lpfll7v5hcqtkxl6l"
platform_name = "LinkedIn"


class TimeRange(Enum):
    """
    Enumeration of available time range filters for LinkedIn job searches.

    Values:
        PAST_24_HOURS
        PAST_WEEK
        PAST_MONTH
        ANY_TIME
    """

    PAST_24_HOURS = "Past 24 hours"
    PAST_WEEK = "Past week"
    PAST_MONTH = "Past month"
    ANY_TIME = "Any time"


class JobType(Enum):
    """
    Enumeration of available job types for LinkedIn job searches.

    Values:
        FULL_TIME
        PART_TIME
        CONTRACT
        TEMPORARY
        VOLUNTEER
    """

    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    VOLUNTEER = "Volunteer"


class ExperienceLevel(Enum):
    """
    Enumeration of available experience levels for LinkedIn job searches.

    Values:
        INTERNSHIP
        ENTRY_LEVEL
        ASSOCIATE
        MID_SENIOR_LEVEL
        DIRECTOR
    """

    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry level"
    ASSOCIATE = "Associate"
    MID_SENIOR_LEVEL = "Mid-Senior level"
    DIRECTOR = "Director"


class Remote(Enum):
    """
    Enumeration of available work arrangements for LinkedIn job searches.

    Values:
        ON_SITE
        REMOTE
        HYBRID
    """

    ON_SITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"


@dataclass(frozen=True)
class LinkedInParams:
    """
    Represents LinkedIn job search parameters with predefined values.

    This class encapsulates the configuration parameters needed for
    scraping job listings from LinkedIn, with immutable default values
    specific to the Philippines market.

    Args:
        date_range (DateRange): The time period for which to search job listings.

    Attributes:
        location (str): Geographic location for job search, defaults to "philippines".
        keywords (str): Search terms for job listings, defaults to "software development".
        country (str): Country code for search region, defaults to "PH".
        date_range (DateRange): Time range filter for job listings.

    Raises:
        ValueError: If location or keywords are empty or invalid strings.

    Example:
        >>> from constants.date_range import DateRange
        >>> params = LinkedInParams(DateRange.PAST_WEEK)
        >>> search_params = params.to_dict()
    """

    location: str = field(default="philippines", init=False)
    keywords: str = field(default="software development", init=False)
    country: str = field(default="PH", init=False)
    date_range: DateRange

    def __init__(self, date_range: DateRange, keywords: str = None):
        object.__setattr__(self, 'date_range', date_range)
        if keywords and isinstance(keywords, str) and keywords.strip():
            object.__setattr__(self, 'keywords', keywords.strip())
        # If keywords is None or empty, the default value from field() will be used

    def __post_init__(self):
        """
        Validate fields and handle date range conversion after initialization.

        This method performs validation on the location and keywords fields,
        and handles special cases for date range conversion to LinkedIn's format.

        Raises:
            ValueError: If location or keywords are empty or invalid strings.

        Note:
            LinkedIn does not support 15-day ranges, so PAST_15_DAYS is
            automatically converted to PAST_WEEK.
        """
        log = get_logger("LinkedIn")

        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")
            raise

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            raise

        if self.date_range == DateRange.PAST_15_DAYS:
            log.warning(
                "LinkedIn does not provide 2 weeks search, searching for last week instead"
            )
            object.__setattr__(self, "date_range", DateRange.PAST_WEEK)

        # if self.job_type and not isinstance(self.job_type, JobType):
        #     log.warning(
        #         f"job_type must be an instance of JobType Enum, got {type(self.job_type)}"
        #     )
        # if self.experience_level and not isinstance(self.experience_level, ExperienceLevel):
        #     log.warning(
        #         f"experience_level must be an instance of ExperienceLevel Enum, got {type(self.experience_level)}"
        #     )
        # if self.remote and not isinstance(self.remote, Remote):
        #     log.warning(
        #         f"remote must be an instance of Remote Enum, got {type(self.remote)}"
        #     )

    def to_dict(self) -> Dict:
        """
        Convert the parameters to a dictionary format.

        Returns:
            Dict: Dictionary containing all search parameters formatted for LinkedIn API.
                Keys include: location, keyword, country, time_range.

        Example:
            >>> params = LinkedInParams(DateRange.PAST_WEEK)
            >>> config_dict = params.to_dict()
            >>> print(config_dict['location'])
            'philippines'
        """
        return {
            "location": self.location,
            "keyword": self.keywords,
            "country": self.country,
            "time_range": self.date_range.value,
        }

    def get_dataset_id(self):
        """
        Retrieve the BrightData dataset identifier.

        Returns:
            str: The unique identifier for the LinkedIn dataset in BrightData.

        Example:
            >>> params = LinkedInParams(DateRange.PAST_WEEK)
            >>> dataset_id = params.get_dataset_id()
        """
        return dataset_id

    def get_platform_name(self):
        """
        Retrieve the platform identifier.

        Returns:
            str: The platform name ("LinkedIn").

        Example:
            >>> params = LinkedInParams(DateRange.PAST_WEEK)
            >>> platform = params.get_platform_name()
            >>> print(platform)
            'LinkedIn'
        """
        return platform_name

    def __dict__(self):
        """
        Provide dictionary representation of parameters.

        Returns:
            Dict: Dictionary containing all search parameters.
                Equivalent to to_dict() method output.
        """
        return self.to_dict()

    def __repr__(self):
        """
        Custom string representation of LinkedInParams.

        Returns:
            str: A clean string representation showing just the values.
        """
        return (
            f"LinkedInParams("
            f"location='{self.location}', "
            f"keyword='{self.keywords}', "
            f"country='{self.country}', "
            f"time_range='{self.date_range}')"
        )
