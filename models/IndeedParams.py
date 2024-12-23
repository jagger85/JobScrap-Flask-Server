from dataclasses import dataclass, field
from typing import Dict
from logger.logger import get_logger
from constants import DateRange

dataset_id = "gd_l4dx9j9sscpvs7no2"
platform_name = "Indeed"


@dataclass(frozen=True)
class IndeedParams:
    """
    Represents Indeed job search parameters with predefined values.

    This class encapsulates the configuration parameters needed for
    scraping job listings from Indeed, with immutable default values
    specific to the Philippines market.

    Args:
        date_range (DateRange): The time period for which to search job listings.

    Attributes:
        location (str): Geographic location for job search, defaults to "philippines".
        keywords (str): Search terms for job listings, defaults to "software developer".
        country (str): Country code for Indeed domain, defaults to "PH".
        domain (str): Indeed domain to search, defaults to "ph.indeed.com".
        _time_range (str): Internal representation of date range in Indeed format.

    Example:
        >>> from constants.date_range import DateRange
        >>> params = IndeedParams(DateRange.PAST_WEEK)
        >>> search_params = params.to_dict()
    """

    date_range: DateRange
    location: str = field(default="philippines", init=False)
    keywords: str = field(default="software developer", init=False)
    country: str = field(default="PH", init=False)
    domain: str = field(default="ph.indeed.com", init=False)
    date_posted: str = field(init=False)

    def __init__(self, date_range: DateRange, keywords: str = None):
        object.__setattr__(self, 'date_range', date_range)
        object.__setattr__(self, 'date_posted', self._convert_date_range(date_range))
        
        if keywords and isinstance(keywords, str) and keywords.strip():
            object.__setattr__(self, 'keywords', keywords.strip())
        # If keywords is None or empty, the default value from field() will be used

    def __post_init__(self):
        """
        Validate fields and convert date range after initialization.

        This method performs validation on the location and keywords fields,
        and converts the DateRange enum to Indeed's specific time range format.

        Raises:
            ValueError: If location or keywords are empty or invalid strings.
        """
        log = get_logger("Indeed")

        # Convert date range to Indeed's format
        object.__setattr__(
            self, "date_posted", self._convert_date_range(self.date_range)
        )

        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")
            raise ValueError("Location must be a non-empty string")

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            raise ValueError("Keywords must be a non-empty string")
        
        if self.date_range == DateRange.PAST_15_DAYS:
            log.warning(
                "Indeed does not provide 15 days search, searching for 14 days instead"
            )
        if self.date_range == DateRange.PAST_MONTH:
            log.warning(
                "Indeed does not provide a month search, searching for last 14 days instead"
            )

    @staticmethod
    def _convert_date_range(date_range: DateRange) -> str:
        """
        Convert DateRange enum to Indeed's date filter format.

        Args:
            date_range (DateRange): Enum value representing the desired time range.

        Returns:
            str: Indeed-specific string format for date filtering.
                Possible values: 'Last 24 hours', 'Last 7 days', 'Last 14 days'.

        Example:
            >>> time_range = IndeedParams._convert_date_range(DateRange.PAST_WEEK)
            >>> print(time_range)
            'Last 7 days'
        """
        date_range_mapping = {
            DateRange.PAST_24_HOURS: "Last 24 hours",
            DateRange.PAST_WEEK: "Last 7 days",
            DateRange.PAST_15_DAYS: "Last 14 days",
            DateRange.PAST_MONTH: "Last 14 days",  # Adapted for Indeed's limitations
        }
        return date_range_mapping[date_range]

    def to_dict(self) -> Dict:
        """
        Convert the parameters to a dictionary format.

        Returns:
            Dict: Dictionary containing all search parameters formatted for Indeed API.
                Keys include: country, domain, location, keyword_search, date_posted.

        Example:
            >>> params = IndeedParams(DateRange.PAST_WEEK)
            >>> config_dict = params.to_dict()
            >>> print(config_dict['location'])
            'philippines'
        """
        return {
            "country": self.country,
            "domain": self.domain,
            "location": self.location,
            "keyword_search": self.keywords,
            "date_posted": self.date_posted,
        }

    def get_dataset_id(self):
        """
        Retrieve the BrightData dataset identifier.

        Returns:
            str: The unique identifier for the Indeed dataset in BrightData.

        Example:
            >>> params = IndeedParams(DateRange.PAST_WEEK)
            >>> dataset_id = params.get_dataset_id()
        """
        return dataset_id

    def get_platform_name(self):
        """
        Retrieve the platform identifier.

        Returns:
            str: The platform name ("Indeed").

        Example:
            >>> params = IndeedParams(DateRange.PAST_WEEK)
            >>> platform = params.get_platform_name()
            >>> print(platform)
            'Indeed'
        """
        return platform_name

    def __dict__(self):
        """
        Provide dictionary representation of parameters.

        Returns:
            Dict: Dictionary containing all search parameters.
                Equivalent to to_dict() method output.
        """

    def __repr__(self):
        """
        Custom string representation of IndeedParams.

        Returns:
            str: A clean string representation showing just the values.
        """
        return (
            f"IndeedParams("
            f"location='{self.location}', "
            f"keyword_search='{self.keywords}', "
            f"country='{self.country}', "
            f"domain='{self.domain}', "
            f"date_posted='{self.date_posted}')"
        )
