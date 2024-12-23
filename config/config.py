from typing import List, Optional
from constants.date_range import DateRange
from constants.platforms import Platforms


class Config:
    """
    A singleton configuration class that centralizes all configuration settings.

    This class manages global configuration settings including chrome driver,
    date ranges, keywords, storage settings, user identification, and platforms
    to scrape. It ensures only one instance exists throughout the application.

    Args:
        None

    Returns:
        Config: The singleton instance of the configuration class.

    Raises:
        None

    Example:
        >>> config = Config()
        >>> config.keywords = "python developer"
        >>> config.init_chrome_driver(headless=True)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._initialize_default_values(cls._instance)
        return cls._instance

    @staticmethod
    def _initialize_default_values(instance):
        # Chrome driver
        instance._chrome_driver = None

        # Date range - using DateRange enum
        instance._date_range = DateRange.PAST_24_HOURS

        # Keywords for search
        instance._keywords = ""

        # Storage configuration - already using StorageType enum
        instance._storage_type = StorageType.JSON
        instance._storage = StorageFactory.get_storage_handler(instance._storage_type)

        # User identification
        instance._user_id = None

        # Platforms to scrape
        instance._platforms = []

        # Platform URLs
        instance._kalibrr_url = "https://www.kalibrr.com/home/co/Philippines/i/it-and-software?sort=Freshness"
        instance._jobstreet_url = "https://ph.jobstreet.com"

    # Date range properties
    @property
    def date_range(self) -> DateRange:
        """
        Get the date range filter for job searches.

        This property defines the time period for filtering job listings.

        Returns:
            DateRange: The enum value representing the date range filter.

        Example:
            >>> config = Config()
            >>> config.date_range = DateRange.PAST_WEEK
        """
        return self._date_range

    @date_range.setter
    def date_range(self, date_range: DateRange):
        self._date_range = date_range

    # Keywords properties
    @property
    def keywords(self) -> str:
        """
        Get the search keywords string.

        This property contains the keywords used for job searching across platforms.

        Returns:
            str: Space-separated keywords for job search.

        Example:
            >>> config = Config()
            >>> config.keywords = "python developer"
            >>> print(config.keywords)
            "python developer"
        """
        return self._keywords

    @keywords.setter
    def keywords(self, keywords: str):
        self._keywords = keywords

    @property
    def storage(self):
        return self._storage

    # User ID properties
    @property
    def user_id(self) -> Optional[str]:
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: str):
        self._user_id = user_id

    # Platforms properties
    @property
    def platforms(self) -> List[Platforms]:
        """
        Get the list of platforms to scrape.

        This property contains the platforms used for job scraping.

        Returns:
            List[Platforms]: List of Platforms enum members for scraping.

        Example:
            >>> config = Config()
            >>> config.platforms = [Platforms.KALIBRR, Platforms.JOBSTREET]
            >>> print(config.platforms)
            [Platforms.KALIBRR, Platforms.JOBSTREET]
        """
        return self._platforms

    @platforms.setter
    def platforms(self, platforms: List[Platforms]):
        self._platforms = platforms

    # Kalibrr URL properties
    @property
    def kalibrr_url(self) -> str:
        """
        Get the base URL for Kalibrr platform.

        Returns:
            str: The base URL for Kalibrr job platform.

        Example:
            >>> config = Config()
            >>> print(config.kalibrr_url)
            "https://www.kalibrr.com"
        """
        return self._kalibrr_url

    @kalibrr_url.setter
    def kalibrr_url(self, url: str):
        self._kalibrr_url = url

    # Jobstreet URL properties
    @property
    def jobstreet_url(self) -> str:
        """
        Get the base URL for Jobstreet platform.

        Returns:
            str: The base URL for Jobstreet job platform.

        Example:
            >>> config = Config()
            >>> print(config.jobstreet_url)
            "https://www.jobstreet.com.ph"
        """
        return self._jobstreet_url

    @jobstreet_url.setter
    def jobstreet_url(self, url: str):
        self._jobstreet_url = url

    # Add these after other properties
    @property
    def listings(self):
        """
        Get the current job listings from the latest scraping operation.

        Returns:
            list: List of job listings or None if no scraping has been performed
        """
        if not hasattr(self, "_listings"):
            self._listings = None
        return self._listings

    @listings.setter
    def listings(self, value):
        self._listings = value

    def reset_to_defaults(self):
        """
        Reset all configuration values to their default state.
        Called after completing an operation to prepare for the next one.
        """
        # Initialize state management using the same pattern as Operation class

        # Reset platform states and notify clients

        # Reset all other values
        self._chrome_driver = None
        self._date_range = DateRange.PAST_24_HOURS
        self._keywords = ""
        self._user_id = None
        self._platforms = []
        self._listings = None
