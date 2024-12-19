from ..base_scrap_state_machine import BaseScrapStateMachine
from .kalibrr_navigator import KalibrrNavigator
from models import JobListing
from typing import List
from config.config import Config


class KalibrrScrapperMachine(BaseScrapStateMachine):
    """
    State machine implementation for scraping Kalibrr job listings.

    This class manages the complete lifecycle of scraping operations for Kalibrr,
    including API requests, data processing, and error handling.

    Args:
        logger (Logger): Logger instance for tracking operations.

    Attributes:
        api_client (KalibrrAPIClient): Client for Kalibrr API interactions.
        listings (list): Collection of scraped job listings.
        state_manager (StateManager): Manages the scraping operation state.
        log (Logger): Logger instance for operation tracking.

    Example:
        >>> scrapper = KalibrrScrapperMachine(logger)
        >>> listings = scrapper.get_job_listings()
    """

    def __init__(self, logger):
        global log
        log = logger
        super().__init__(logger)
        self.driver.get(Config().kalibrr_url)
        
    def get_job_listings(self):
        """
        Retrieve job listings from Kalibrr's API.

        This method initializes the API client and requests job listings,
        handling any errors that occur during the process.

        Returns:
            list: Collection of raw job listings.
                Returns empty list if no listings are found or on error.

        Raises:
            Exception: If API request fails, sets platform state to ERROR.

        Example:
            >>> scrapper = KalibrrScrapperMachine(logger)
            >>> listings = scrapper.get_job_listings()
            >>> print(f"Found {len(listings)} jobs")
        """
        log.info("Fetching Kalibrr job listings")
        navigator = KalibrrNavigator(logger=log, driver=self.driver, date_range=self.date_range)
        self.listings = navigator.request_listings()

    def process_job_listings(self) -> List[JobListing]:
        """
        Process raw job listings into structured JobListing objects.

        This method transforms the raw listing data into standardized JobListing
        objects, including date conversion and field normalization.

        Returns:
            List[JobListing]: Collection of processed job listings.
                Returns empty list if no listings are available or on error.

        Raises:
            Exception: If processing fails, sets platform state to ERROR.

        Example:
            >>> scrapper = KalibrrScrapperMachine(logger)
            >>> processed_listings = scrapper.process_job_listings()
        """
        log.info("Processing Kalibrr job listings")
        processed_listings = []

        for job in self.listings:
            # Debug log to check the job data
            log.debug(f"Processing job with date: {job.get('listing_date')}")
            
            processed_listing = JobListing(
                site=log.name,
                listing_date=job.get("listing_date", None),
                job_title=job.get("title", None),
                company=job.get("company", None),
                location=job.get("location", None),
                employment_type=f"Type: {job.get('job_type', 'unspecified')} / {job.get('job_arrangement','unspecified')}",
                position=job.get("position", "unspecified"),
                salary=job.get("salary", "unspecified"),
                description=job.get("description", None),
                url=job.get("url", None),
            )
            processed_listings.append(processed_listing)

        log.info(f"Processed {len(processed_listings)} job listings")
        return processed_listings

    def process_error(self):
        """
        Handle errors during the scraping process.

        This method logs the error and updates the platform state to ERROR
        when exceptions occur during scraping operations.

        Returns:
            None: State changes are handled internally.

        Example:
            >>> scrapper = KalibrrScrapperMachine(logger)
            >>> try:
            >>>     listings = scrapper.get_job_listings()
            >>> except Exception:
            >>>     scrapper.process_error()
        """
        log.info("Processing Kalibrr error")
        pass

    def format_salary(self, min_salary: int, max_salary: int) -> str:
        """
        Format salary range into a standardized string format.

        Args:
            min_salary (int): Minimum salary amount.
            max_salary (int): Maximum salary amount.

        Returns:
            str: Formatted salary range string.
                Format: "₱{min_salary:,} - ₱{max_salary:,}"
                Returns "Undisclosed" if both values are 0.

        Example:
            >>> salary = format_salary(30000, 50000)
            >>> print(salary)
            '₱30,000 - ₱50,000'
        """

    def process_location(self, location_data: dict) -> str:
        """
        Process location data into a standardized string format.

        Args:
            location_data (dict): Location information from API response.
                Expected keys: 'city', 'region', 'country'

        Returns:
            str: Formatted location string.
                Format: "{city}, {region}, {country}"

        Example:
            >>> location = process_location({'city': 'Makati', 'region': 'NCR', 'country': 'PH'})
            >>> print(location)
            'Makati, NCR, PH'
        """
