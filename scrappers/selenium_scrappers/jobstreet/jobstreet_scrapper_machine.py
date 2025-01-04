from ..base_scrap_state_machine import BaseScrapStateMachine
from .jobstreet_navigator import JobstreetNavigator
from typing import List
from models import JobListing
from datetime import datetime, timedelta
import re
from constants import DateRange, jobstreet_url
from logger.logger import get_logger
from services import update_operation_listings_count, update_operation_info_message


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
    def __init__(self, days: str = "1", keywords: str = None , task_id: str = None, user_id: str = None):
        global log
        log = get_logger("Jobstreet")
        super().__init__(log)
        self.days = days
        self.keywords = keywords
        self.task_id = task_id
        self.user_id = user_id
        # Set initial state to PROCESSING when starting scraping

        self.driver.get(self.build_jobstreet_url())
        log.info("Retrieving job listings from Jobstreet, this may take a few minutes…")
        update_operation_info_message(self.user_id, self.task_id, "Retrieving job listings from Jobstreet, this may take a few minutes…")
    def build_keywords(self) -> str:
        if self.keywords:
            # Replace spaces with hyphens and append "-jobs"
            formatted_keywords = f"{self.keywords.replace(' ', '-')}-jobs"
            return f"{formatted_keywords}"
        return ""
    
    
    
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
 
        base_url = jobstreet_url
        classification = '6263%2C6281'
        subclassification = '6268%2C6273%2C6284%2C6286%2C6287%2C6290%2C6302'
        if self.keywords:
            log.debug(f"Using keywords: {self.build_keywords()}")
            url = f"{base_url}/{self.build_keywords()}?classification={classification}&daterange={self.days}&subclassification={subclassification}"
            log.debug(url)
            return url
        else:
            url = f"{base_url}/jobs?classification={classification}&daterange={self.days}&subclassification={subclassification}"
            log.debug(url)
            return url

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
            navigator = JobstreetNavigator(logger=log, driver=self.driver, user_id=self.user_id, task_id=self.task_id)
            self.listings = navigator.request_listings()
            if not self.listings:
                log.warning("No listings found")
                return []
            return self.listings
        except Exception as e:
            log.error(f"Error fetching job listings: {str(e)}")
            update_operation_info_message(self.user_id, self.task_id, "Error fetching job listings: " + str(e))
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

            log.info(f"Total listings found on Jobstreet: {len(processed_listings)}")

            return processed_listings

        except Exception as e:
            log.error(f"Error processing job listings: {str(e)}")

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
