from .kalibrr_home_page import KalibrrHomePage
from .kalibrr_job_page import KalibrrJobPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By


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
    def __init__(self,logger, driver):
        global log
        log = logger
        self.driver = driver
        self.home_page = KalibrrHomePage(driver=self.driver,logger=log)
        self.job_listings = []


    def request_listings(self):
        
        self._load_elements()
        self._get_job_listings()
        self._navigate_to_listings()

        return self.job_listings

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
        Navigate to each listings URL in the job_listings and collect listings details.

        This method iterates through the listings listings, navigates to each listings's URL,
        and retrieves relevant listings information such as description, posting date,
        and validity period. It tracks the success and failure counts for navigation.

        Returns:
            None

        Example:
            >>> navigator = KalibrrNavigator(driver)
            >>> navigator.navigate_to_jobs()
            Collected 50 listings descriptions with 2 failures.
        """
        success_count = 0
        failure_count = 0
        total_jobs = len(self.job_listings)
        
        # Use a list to track indices that need to be removed
        indices_to_remove = []
        
        for index, listing in enumerate(self.job_listings):
            log.progress(f'🛰️  Loading {index + 1}/{total_jobs} descriptions')
            try:
                # Create job page instance before navigation
                job_page = KalibrrJobPage(self.driver)
                
                # Add timeout for page load
                self.home_page.driver.set_page_load_timeout(30)
                self.home_page.driver.get(listing['url'])
                
                # Batch the data collection
                job_data = {
                    'description': job_page.get_job_description(),
                    'listing_posted_date': job_page.get_job_listing_date(),
                    'valid_through': job_page.get_valid_through()
                }
                
                # Update listing dictionary with collected data
                listing.update(job_data)
                success_count += 1

            except Exception as e:
                failure_count += 1
                print("\r")
                log.error(f"Error navigating to listing URL: {listing['url']}")
                log.debug(f'Error {str(e)}')
                
                # Add failed listing index to removal list
                indices_to_remove.append(index)
                
                # Add failed listing URL to a list for potential retry
                if not hasattr(self, 'failed_jobs'):
                    self.failed_jobs = []
                self.failed_jobs.append(listing['url'])

        # Remove failed listings in reverse order to maintain correct indices
        for index in sorted(indices_to_remove, reverse=True):
            self.job_listings.pop(index)
            log.info('Invalid listing removed')


        # Update total_jobs count after removals
        total_jobs = len(self.job_listings)

        if failure_count == 0:
            log.progress_complete('🛰️  All listings descriptions collected successfully.')
        else:
            log.progress_complete(
                f'🛰️  Collected {success_count}/{total_jobs} descriptions with {failure_count} failures.'
            )

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