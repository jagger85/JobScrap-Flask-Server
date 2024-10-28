from .kalibrr_home_page import KalibrrHomePage
from .kalibrr_job_page import KalibrrJobPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By

class KalibrrNavigator:
    def __init__(self,logger, driver):
        global log
        log = logger
        self.driver = driver
        self.home_page = KalibrrHomePage(driver=self.driver,logger=log)
        self.job_listings = []


    def request_listings(self):
        
        self._load_elements()
        self._get_job_listings()
        self._navigate_to_jobs()

        return self.job_listings

    def _load_elements(self, timeout=10):
        """
        Load more job listings by clicking the 'Load More' button repeatedly.

        This method continuously clicks the 'Load More' button on the home_page to reveal
        additional job listings until no more entries can be loaded or an exception occurs.

        Args:
            timeout (int): The maximum time to wait for elements to become clickable
            or for new job listings to appear, in seconds. Defaults to 10.

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
                
                # Get the current number of job listings
                initial_job_count = len(self.home_page.driver.find_elements(By.XPATH, self.home_page.locators["JobListingCard"]["locator"]))
                
                # Click the button
                load_more_button.click()
                
                # Wait for new job listings to appear
                WebDriverWait(self.home_page.driver, timeout).until(
                    lambda driver: len(driver.find_elements(By.XPATH, self.home_page.locators["JobListingCard"]["locator"])) > initial_job_count
                )
                
            except (TimeoutException, StaleElementReferenceException, NoSuchElementException) as e:
                log.error(f"Finished loading jobs. Reason: {str(e)}")
                break
        
        

    def _get_job_listings(self):
        """
        Retrieve job listings and add them to the job_listings attribute.

        This method calls get_job_listing_cards() from the home page and extends
        the job_listings list with the returned job listings.

        Returns:
            None

        Example:
            >>> navigator = KalibrrNavigator(driver)
            >>> navigator.get_job_listings()
            Retrieved 50 job listings. Total listings: 50
        """
        new_listings = self.home_page.get_job_listing_cards()
        self.job_listings.extend(new_listings)
        log.info(f"Retrieved {len(new_listings)} job listings")

    def _navigate_to_jobs(self):
        for index, job in enumerate(self.job_listings, 1):
            log.progress(f'🛰️  Loading {index}/{len(self.job_listings)} descriptions')
            try:
                self.home_page.driver.get(job['url'])
                job_page = KalibrrJobPage(self.driver)
                job_description = job_page.get_job_description()
                job['description'] = job_description
                job_listing_date = job_page.get_job_listing_date()
                job['listing_posted_date'] = job_listing_date
                valid_through = job_page.get_valid_through()
                job['valid_through'] = valid_through

            except Exception:
                print("\v")
                log.error(f"Error navigating to job URL: {job['url']}")
        log.progress_complete('🛰️  All job descriptions collected')
