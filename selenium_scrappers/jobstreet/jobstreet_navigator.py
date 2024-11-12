from .jobstreet_home_page import JobstreetHomePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class JobstreetNavigator:
    """
    Controls the navigation and scraping flow for Jobstreet job listings.

    This class manages the complete process of collecting job listings from
    Jobstreet, including pagination and detailed information extraction.

    Args:
        logger (Logger): Logger instance for tracking operations.
        driver (WebDriver): Selenium WebDriver instance for browser automation.

    Attributes:
        driver (WebDriver): WebDriver instance for page interactions.
        page (str): Current page URL.
        home_page (JobstreetHomePage): Handler for home page interactions.
        job_listings (list): Collection of scraped job listings.

    Example:
        >>> from selenium import webdriver
        >>> driver = webdriver.Chrome()
        >>> navigator = JobstreetNavigator(logger, driver)
        >>> listings = navigator.request_listings()
    """

    def __init__(self, logger, driver,):
        global log
        log = logger
        self.driver = driver
        self.page = driver.current_url
        self.home_page = JobstreetHomePage(driver=self.driver, logger=log)
        self.job_listings = []

    def request_listings(self):
        """
        Main method to control the scraping flow.

        This method orchestrates the complete scraping process, including
        pagination and detailed information collection for each job listing.

        Returns:
            list: Collection of job listings, each containing detailed information.
                Returns empty list if no listings are found or on error.

        Raises:
            None: All exceptions are caught and handled internally.

        Example:
            >>> navigator = JobstreetNavigator(logger, driver)
            >>> listings = navigator.request_listings()
            >>> print(f"Collected {len(listings)} job listings")
        """
        try:
            log.debug("Starting job listings collection process")
            # Assuming the driver is already at the correct URL
            
            while True:
                # Get listing IDs from current page
                listing_ids = self.home_page.get_listings_cards_id()
                log.debug(f"Found {len(listing_ids)} listings on current page")
                
                if not listing_ids:
                    log.debug("No more listings found within date limit")
                    break
                
                # Process each listing
                for index, listing_id in enumerate(listing_ids, start=1):
                    log.debug(f"Processing listing {index} of {len(listing_ids)}")
                    listing_details = self._get_listing_details(listing_id)
                    
                    if listing_details:
                        listing_details['listing_id'] = listing_id
                        self.job_listings.append(listing_details)
                        log.debug(f"Successfully collected details for listing {listing_id}")
                    else:
                        log.error(f"Failed to collect details for listing {listing_id}")
                    
                
                # Extract the base URL without the page parameter
                base_url = self.page.split("page=")[0]
                
                # Extract the current page number from the URL or set to 1 if not present
                current_page = int(self.page.split("page=")[-1]) if "page=" in self.page else 1
                next_page = current_page + 1

                # Construct the new URL with the incremented page number
                if "page=" in self.page:
                    new_url = base_url + f"page={next_page}"
                    log.debug(f'Next page: {new_url}')
                else:
                    new_url = self.page + f"&page={next_page}"
                    log.debug(f'Next page: {new_url}')


                # Check if the new page exists by attempting to load it
                self.driver.get(new_url)
                if "No results found" in self.driver.page_source:  # Adjust this condition based on actual page content
                    log.debug("No more pages to process")
                    break

                # Update self.page with the new URL
                self.page = new_url
                log.debug(f"Navigated to page {next_page}")
            
            log.info(f"Retrieved {len(self.job_listings)} listings for Jobstreet")
            return self.job_listings
           
        except Exception as e:
            log.error(f"Error in request_listings: {str(e)}")
            return []

    def _get_listing_details(self, listing_id):
        """
        Extract detailed information for a specific job listing.

        This method navigates to the job detail page and extracts all available
        information about the position.

        Args:
            listing_id (str): Unique identifier for the job listing.

        Returns:
            dict: Dictionary containing job details with keys:
                - title: Job title
                - company: Company name
                - location: Job location
                - work_type: Type of employment
                - description: Full job description
                - listing_date: Date posted
                - salary: Salary information (if available)
                - job_link: URL of the job listing
                - listing_id: Original listing ID
                Returns None if essential fields are missing or on error.

        Example:
            >>> navigator = JobstreetNavigator(logger, driver)
            >>> details = navigator._get_listing_details("123456")
            >>> if details:
            >>>     print(f"Found job: {details['title']}")
        """
        try:
            log.debug(f"Attempting to get details for listing {listing_id}")
            detail_url = f"https://www.jobstreet.com.ph/job/{listing_id}"
            log.debug(f"Navigating to: {detail_url}")
            self.driver.get(detail_url)
            
            # Wait for the details page to load
            try:
                log.debug("Waiting for job details page to load...")
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-automation='jobDetailsPage']"))
                )
                log.debug("Job details page loaded")
                
                # Wait for title to be present as it's a key element
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[@data-automation='job-detail-title']"))
                )
                
                # Extract details using direct element access
                details = {}
                try:
                    details['title'] = self.driver.find_element(By.XPATH, "//h1[@data-automation='job-detail-title']").text
                    details['company'] = self.driver.find_element(By.XPATH, "//span[@data-automation='advertiser-name']").text
                    details['location'] = self.driver.find_element(By.XPATH, "//span[@data-automation='job-detail-location']").text
                    details['work_type'] = self.driver.find_element(By.XPATH, "//span[@data-automation='job-detail-work-type']").text
                    details['description'] = self.driver.find_element(By.XPATH, "//div[@data-automation='jobAdDetails']").text
                    details['listing_date'] = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Posted')]").text
                    details['job_link'] = self.driver.current_url
                except NoSuchElementException as e:
                    log.error(f"Error extracting element: {str(e)}")
                    return None
                
                # Special handling for salary
                details['salary'] = None
                salary_locators = [
                    "//span[@data-automation='job-detail-add-expected-salary']",
                    "//span[@data-automation='job-detail-salary']"
                ]
                for salary_xpath in salary_locators:
                    try:
                        details['salary'] = self.driver.find_element(By.XPATH, salary_xpath).text
                        log.debug(f"Extracted salary: {details['salary']}")
                        break
                    except NoSuchElementException:
                        log.debug(f"Salary element not found with xpath: {salary_xpath}")
                
                # Validate essential fields
                if not all([details['title'], details['company'], details['description']]):
                    log.error("Missing essential fields")
                    return None
                    
                log.debug("Successfully extracted job details")
                return details
                
            except Exception as wait_error:
                log.error(f"Error waiting for or extracting details: {str(wait_error)}")
                # Log the current page source for debugging
                log.debug("Current page source:")
                log.debug(self.driver.page_source[:500])  # First 500 chars
                return None
                
        except Exception as e:
            log.error(f"Unexpected error getting listing details: {str(e)}")
            return None
