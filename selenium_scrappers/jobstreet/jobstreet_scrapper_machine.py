from ..base_scrap_state_machine import BaseScrapStateMachine
from .jobstreet_navigator import JobstreetNavigator
from typing import List
from models.JobListing import JobListing
from datetime import datetime, timedelta
import re
from config.config import Config
from constants.date_range import DateRange
from constants.platforms import Platforms
from constants.platform_states import PlatformStates
from logger.logger import get_logger


class JobstreetScrapperMachine(BaseScrapStateMachine):
    """
    State machine implementation for scraping Jobstreet job listings.

    This class manages the complete lifecycle of scraping operations for Jobstreet,
    including URL construction, data collection, and error handling.

    Attributes:
        driver (WebDriver): Selenium WebDriver instance for browser automation.
        listings (list): Collection of scraped job listings.
        state_manager (StateManager): Manages the scraping operation state.
        log (Logger): Logger instance for operation tracking.

    Example:
        >>> scrapper = JobstreetScrapperMachine()
        >>> listings = scrapper.get_job_listings()
    """
    def __init__(self):
        global log
        log = get_logger("Jobstreet")
        super().__init__(log)
        
        
        # Set initial state to PROCESSING when starting scraping
        self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.PROCESSING)

        self.driver.get(self.build_jobstreet_url())
        log.info("Retrieving job listings from Jobstreet, this may take a few minutes…")

    def build_jobstreet_url(self) -> str:
        """
        Construct the Jobstreet URL with appropriate search parameters.

        This method builds a URL with classification, subclassification, and
        date range parameters for job searching.

        Returns:
            str: Complete URL for Jobstreet job search.

        Example:
            >>> scrapper = JobstreetScrapperMachine()
            >>> url = scrapper.build_jobstreet_url()
            >>> print(url)
            'https://www.jobstreet.com.ph/jobs?classification=...'
        """
        date_range_mapping = {
            DateRange.PAST_24_HOURS: "1",
            DateRange.PAST_WEEK: "7",
            DateRange.PAST_15_DAYS: "15",
            DateRange.PAST_MONTH: "31"
        }
        
        base_url = Config().jobstreet_url
        date_range_value = date_range_mapping.get(self.date_range)
        classification = '6263%2C6281'
        subclassification = '6268%2C6273%2C6284%2C6286%2C6287%2C6290%2C6302'
        log.debug(f"Jobstreet scrapped url: {base_url}?classification={classification}&daterange={date_range_value}&subclassification={subclassification}")
        
        return f"{base_url}?classification={classification}&daterange={date_range_value}&subclassification={subclassification}"

    def get_job_listings(self):
        """
        Retrieve job listings from Jobstreet.

        This method initializes the navigator and requests job listings,
        handling any errors that occur during the process.

        Returns:
            list: Collection of job listings.
                Returns empty list if no listings are found or on error.

        Example:
            >>> scrapper = JobstreetScrapperMachine()
            >>> listings = scrapper.get_job_listings()
            >>> print(f"Found {len(listings)} jobs")
        """
        try:
            navigator = JobstreetNavigator(logger=log, driver=self.driver)
            self.listings = navigator.request_listings()
            if not self.listings:
                log.warning("No listings found")
                return []
            return self.listings
        except Exception as e:
            log.error(f"Error fetching job listings: {str(e)}")
            self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.ERROR)
            return []

    def process_job_listings(self) -> List[JobListing]:
        """
        Process raw job listings into structured JobListing objects.

        This method transforms the raw listing data into standardized JobListing
        objects, including date conversion and field normalization.

        Returns:
            List[JobListing]: Collection of processed job listings.
                Returns empty list if no listings are available or on error.

        Raises:
            Exception: If processing fails, sets platform state to ERROR and re-raises.

        Example:
            >>> scrapper = JobstreetScrapperMachine()
            >>> processed_listings = scrapper.process_job_listings()
        """
        try:
            if not hasattr(self, 'listings') or not self.listings:
                log.warning("No listings found on Jobstreet")
                self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.ERROR)
                return []

            processed_listings = []
            for listing in self.listings:
                processed_listing = JobListing(
                    site=log.name,
                    listing_date=convert_relative_dates_to_absolute(listing.get("listing_date", None)),
                    job_title=listing.get("title", None),
                    company=listing.get("company", None),
                    location=listing.get("location", None),
                    employment_type=listing.get("work_type", "unspecified"),
                    position=listing.get("position", "unspecified"),
                    salary=listing.get("salary", "unspecified"),
                    description=listing.get("description", None),
                    url=listing.get("job_link", None),
                )
                processed_listings.append(processed_listing)

            # Set state to FINISHED after successful processing
            self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.FINISHED)
            log.info(f"Total listings found on Jobstreet: {len(processed_listings)}")

            return processed_listings

        except Exception as e:
            log.error(f"Error processing job listings: {str(e)}")
            self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.ERROR)
            raise

    def process_error(self):
        """
        Handle errors during the scraping process.

        This method logs the error and updates the platform state to ERROR
        when exceptions occur during scraping operations.

        Returns:
            None: State changes are handled internally.

        Example:
            >>> scrapper = JobstreetScrapperMachine()
            >>> try:
            >>>     listings = scrapper.get_job_listings()
            >>> except Exception:
            >>>     scrapper.process_error()
        """
        log.error("Error occurred during Jobstreet scraping")
        self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.ERROR)


def convert_relative_dates_to_absolute(date_str):
    """
    Convert relative date strings to absolute dates in MM-DD-YY format.

    This function parses relative date strings (e.g., "Posted 2h ago") and
    converts them to absolute dates based on the current time.

    Args:
        date_str (str): Relative date string to convert.
            Expected format: "Posted Xm/h/d ago"

    Returns:
        str: Absolute date in MM-DD-YY format.
            Returns None if the date string cannot be parsed.

    Example:
        >>> date = convert_relative_dates_to_absolute("Posted 2h ago")
        >>> print(date)
        '03-20-24'
    """
    now = datetime.now()
    match = re.match(r"Posted (\d+)([mhd]) ago", date_str)
    if match:
        value, unit = match.groups()
        value = int(value)

        if unit == 'm':  # minutes
            date = now - timedelta(minutes=value)
        elif unit == 'h':  # hours
            date = now - timedelta(hours=value)
        elif unit == 'd':  # days
            date = now - timedelta(days=value)

        return date.strftime("%m-%d-%y")
    
    return None  # or raise an exception if the format is not matched
