from .kalibrr_home_page import KalibrrHomePage
from .kalibrr_job_page import KalibrrJobPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from constants.date_range import DateRange
from datetime import datetime, timedelta

class KalibrrNavigator:
    """
    Navigate and manage job listings on the Kalibrr platform.

    This class provides methods to load, retrieve, and navigate through job listings
    on the Kalibrr platform using Selenium WebDriver. It handles loading more listings,
    collecting job details, and managing incomplete listings.

    Attributes:
        driver (WebDriver): The Selenium WebDriver instance used for navigation.
        home_page (KalibrrHomePage): An instance of the KalibrrHomePage for interacting with the home page.
        job_listings (list): A list to store job listings retrieved from the platform.
    """
    def __init__(self, driver, date_range, logger):
        global log
        log = logger
        self.driver = driver 
        self.date_range = date_range 
        self.home_page = KalibrrHomePage(driver=self.driver, logger=log)
        self.job_listings = []


    def request_listings(self):
        """
        Request and process job listings according to the date limit criteria.
        
        Returns:
            list: Filtered job listings that meet the date criteria
        """
        try:
            log.info(f"Starting job listing collection with date range: {self.date_range.value}")
            
            # Load all available listings first
            log.info("Loading all available job listings...")
            self._load_elements()
            
            # Get basic info for all listings
            log.info("Collecting basic information from job cards...")
            self._get_job_listings()
            total_found = len(self.job_listings)
            log.info(f"Found {total_found} total job listings")
            
            # Navigate to each listing to get details and filter by date
            log.info("Starting detailed navigation and date filtering...")
            self._navigate_to_listings()
            
            filtered_count = len(self.job_listings)
            log.info(f"""Collection complete:
                            - Total listings found: {total_found}
                            - Listings within date range: {filtered_count}
                            - Listings filtered out: {total_found - filtered_count}
                    """)
            
            return self.job_listings
            
        except Exception as e:
            log.error(f"Error in request_listings: {str(e)}")
            return self.job_listings

    def _try_load_more(self, timeout=10):
        """
        Attempt to load more listings by clicking the 'Load More' button.
        
        Returns:
            bool: True if more listings were loaded, False otherwise
        """
        try:
            # Store initial listing count
            initial_count = len(self.home_page.driver.find_elements(
                By.XPATH, self.home_page.locators["JobListingCard"]["locator"]
            ))
            
            # Find load more button
            load_more_locator = self.home_page.load_more_jobs_button()
            load_more_buttons = self.home_page.driver.find_elements(By.XPATH, load_more_locator)
            
            if not load_more_buttons:
                return False
                
            # Wait for button to be clickable
            load_more_button = WebDriverWait(self.home_page.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, load_more_locator))
            )
            
            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
            load_more_button.click()
            
            # Wait for new listings
            WebDriverWait(self.home_page.driver, timeout).until(
                lambda driver: len(driver.find_elements(
                    By.XPATH, self.home_page.locators["JobListingCard"]["locator"]
                )) > initial_count
            )
            
            return True
            
        except Exception as e:
            return False

    def _is_within_date_range(self, listing_date):
        """
        Check if the listing date is within the specified date range.
        
        Args:
            listing_date (str): Date string in MM-DD-YY format
            
        Returns:
            bool: True if within range, False otherwise
        """
        try:
            log.debug(f"Parsing date: {listing_date}")
            listing_datetime = datetime.strptime(listing_date, '%m-%d-%y')
            current_date = datetime.now()
            
            # Normalize dates to midnight
            listing_datetime = listing_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if self.date_range == DateRange.PAST_24_HOURS:
                cutoff_date = current_date - timedelta(days=1)
            elif self.date_range == DateRange.PAST_WEEK:
                cutoff_date = current_date - timedelta(days=7)
            elif self.date_range == DateRange.PAST_15_DAYS:
                cutoff_date = current_date - timedelta(days=15)
            else:  # PAST_MONTH
                cutoff_date = current_date - timedelta(days=30)
            
            cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0)
            is_within_range = listing_datetime >= cutoff_date
            log.debug(f"""
    Date comparison:
    - Listing date: {listing_datetime}
    - Cutoff date: {cutoff_date}
    - Date range: {self.date_range}
    - Within range: {is_within_range}
    """)
            
            return is_within_range
            
        except ValueError as e:
            log.error(f"Error parsing date '{listing_date}': {str(e)}")
            return False

    def _load_elements(self, timeout=10):
        """
        Load more listings listings by clicking the 'Load More' button repeatedly.

        This method continuously clicks the 'Load More' button on the home_page to reveal
        additional listings listings until no more entries can be loaded or an exception occurs.

        Args:
            timeout (int): The maximum time to wait for elements to become clickable
            or for new listings listings to appear, in seconds. Defaults to 10.

        Returns:
            None

        Raises:
            None: This method handles all exceptions internally and breaks the loop
            when no more jobs can be loaded.

        Example:
            >>> navigator = KalibrrNavigator(driver)
            >>> navigator.load_more_elements()
            Loaded more jobs. Total jobs: 40
            Loaded more jobs. Total jobs: 80
            No more entries to load.
        """
        while True:
            try:
                # Get the locator for the load more button
                load_more_jobs_button_locator = self.home_page.load_more_jobs_button()
                
                # Check if the button is present
                load_more_buttons = self.home_page.driver.find_elements(By.XPATH, load_more_jobs_button_locator)
                if not load_more_buttons:
                    log.info("No more entries to load")
                    break
                
                # Wait for the load more button to be clickable
                load_more_button = WebDriverWait(self.home_page.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, load_more_jobs_button_locator))
                )
                
                # Get the current number of listings listings
                initial_job_count = len(self.home_page.driver.find_elements(By.XPATH, self.home_page.locators["JobListingCard"]["locator"]))
                
                # Click the button
                load_more_button.click()
                
                # Wait for new listings listings to appear
                WebDriverWait(self.home_page.driver, timeout).until(
                    lambda driver: len(driver.find_elements(By.XPATH, self.home_page.locators["JobListingCard"]["locator"])) > initial_job_count
                )
                
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException) as e:
                log.error(f"Finished loading jobs. Reason: {str(e)}")
                break
        
        

    def _get_job_listings(self):
        """
        Retrieve listings listings and add them to the job_listings attribute.

        This method calls get_job_listing_cards() from the home page and extends
        the job_listings list with the returned listings listings.

        Returns:
            None

        Example:
            >>> navigator = KalibrrNavigator(driver)
            >>> navigator.get_job_listings()
            Retrieved 50 listings listings. Total listings: 50
        """
        new_listings = self.home_page.get_job_listing_cards()
        self.job_listings.extend(new_listings)
        log.info(f"Retrieved {len(new_listings)} listings listings")

    def _navigate_to_listings(self):
        """
        Navigate to each listing URL, collect details, and filter by date range.
        """
        success_count = 0
        filtered_out_count = 0
        failure_count = 0
        total_jobs = len(self.job_listings)
        
        # Use a list to track indices that need to be removed
        indices_to_remove = []
        
        for index, listing in enumerate(self.job_listings):
            log.progress(f'🛰️  Processing {index + 1}/{total_jobs} listings')
            try:
                job_page = KalibrrJobPage(self.driver)
                self.driver.get(listing['url'])
                
                # Get the listing date first
                listing_date = job_page.get_job_listing_date()
                
                # Check if within date range before collecting other data
                if not self._is_within_date_range(listing_date):
                    log.debug(f"Listing date {listing_date} outside range {self.date_range.value}")
                    indices_to_remove.append(index)
                    filtered_out_count += 1
                    continue
                
                # Collect remaining data only for listings within date range
                listing.update({
                    'description': job_page.get_job_description(),
                    'listing_date': listing_date,
                    'valid_through': job_page.get_valid_through()
                })
                success_count += 1

            except Exception as e:
                failure_count += 1
                log.error(f"Error processing listing {listing.get('url', 'Unknown URL')}")
                log.debug(f"{str(e)}")
                indices_to_remove.append(index)
                
                if not hasattr(self, 'failed_jobs'):
                    self.failed_jobs = []
                self.failed_jobs.append(listing.get('url'))

        # Remove filtered and failed listings in reverse order
        for index in sorted(indices_to_remove, reverse=True):
            self.job_listings.pop(index)

        log.info(f"""
Navigation results:
- Successfully processed: {success_count}
- Filtered out (date): {filtered_out_count}
- Failed to process: {failure_count}
- Remaining listings: {len(self.job_listings)}
""")

    def _remove_incomplete_listing(self, listing_index):
        """
        Remove an incomplete listing from the job_listings based on the given index.

        This method checks if the index is valid and removes the corresponding listing
        from the job_listings list. If the index is out of bounds, it logs an error.

        Args:
            listing_index (int): The index of the listing to remove.

        Returns:
            None

        Example:
            >>> navigator = KalibrrNavigator(driver)
            >>> navigator._remove_incomplete_listing(2)
            Removed listing at index 2.
        """
        if 0 <= listing_index < len(self.job_listings):
            removed_listing = self.job_listings.pop(listing_index)
            log.debug(f"Removed listing at index {listing_index}: {removed_listing}")
        else:
            log.error(f"Index {listing_index} is out of bounds. No listing removed.")
