import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from helpers import FileContext

# Define the absolute path to the locators directory
LOCATORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobstreet_locators.json")

class JobstreetHomePage:
    """
    Manages the scraping of job listings from Jobstreet's home page.

    This class handles navigation and data extraction from Jobstreet's job listing
    pages using Selenium WebDriver.

    Args:
        driver (WebDriver): Selenium WebDriver instance for browser automation.
        logger (Logger): Logger instance for tracking operations.

    Attributes:
        driver (WebDriver): WebDriver instance for page interactions.
        locators (dict): JSON configuration containing element locators.
        log (Logger): Logger for operation tracking.

    Example:
        >>> from selenium import webdriver
        >>> driver = webdriver.Chrome()
        >>> page = JobstreetHomePage(driver, logger)
        >>> listings = page.get_listings_cards_id()
    """

    def __init__(self, driver, logger):
        global log
        log = logger
        self.driver = driver
        file = FileContext()
        with file.safe_open(LOCATORS_DIR, "r") as json_file:
            self.locators = json.load(json_file)
        
    def get_listings_cards_id(self):
        """
        Extract all job listing IDs from the current page.

        This method waits for job cards to load and extracts their unique
        identifiers from the data-job-id attribute.

        Returns:
            list: Collection of job listing IDs as strings.
                Returns empty list if no listings are found or on error.

        Raises:
            None: All exceptions are caught and handled internally.

        Example:
            >>> page = JobstreetHomePage(driver, logger)
            >>> ids = page.get_listings_cards_id()
            >>> print(f"Found {len(ids)} job listings")
        """
        try:
            log.debug("Waiting for job cards to load...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.locators["jobListing"]["normalJobCard"]["locator"]))
            )
            
            listing_cards = self.driver.find_elements(By.XPATH, self.locators["jobListing"]["normalJobCard"]["locator"])
            listing_ids = []
            
            for card in listing_cards:
                try:
                    # Get listing ID directly from data attribute
                    listing_id = card.get_attribute('data-job-id')
                    if listing_id:
                        log.debug(f"Extracted listing ID: {listing_id}")
                        listing_ids.append(listing_id)
                    else:
                        log.error("\nCould not find data-job-id attribute")
                        
                except NoSuchElementException as e:
                    log.error(f"Error extracting data from card: {str(e)}")
                    continue
            log.debug("Extracted listings complete")
            return listing_ids
            
        except TimeoutException:
            log.debug("Timeout waiting for job cards to load")
            return []

    def go_to_next_page(self):
        """
        Navigate to the next page of job listings if available.

        This method attempts to find and click the next page button,
        waiting for the new page to load completely.

        Returns:
            bool: True if navigation was successful, False if no next page
                exists or navigation failed.

        Example:
            >>> page = JobstreetHomePage(driver, logger)
            >>> while page.go_to_next_page():
            >>>     listings = page.get_listings_cards_id()
        """
        log.debug(f"Current URL before clicking next: {self.driver.current_url}")
        try:
            next_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.locators["pagination"]["nextButton"]["locator"]))
            )
            
            if next_button.is_enabled():
                
                log.debug("Navigating to next page...")
                next_button.click()
                # Wait for new page to load
                WebDriverWait(self.driver, 10).until(
                    EC.staleness_of(next_button)
                )
                return True
            return False
            
        except (TimeoutException, NoSuchElementException):
            log.debug("No next page button found or page navigation failed")
            return False

    def _extract_listing_details(self):
        """
        Extract detailed information from the current job listing page.

        This method scrapes various fields from the job listing including title,
        company, location, salary, and description.

        Returns:
            dict: Dictionary containing job listing details with keys:
                - title: Job title
                - company: Company name
                - location: Job location
                - work_type: Type of employment
                - description: Full job description
                - listing_date: Date posted
                - salary: Salary information (if available)
                - job_link: Current page URL
                Returns None if essential fields are missing or on error.

        Example:
            >>> page = JobstreetHomePage(driver, logger)
            >>> details = page._extract_listing_details()
            >>> if details:
            >>>     print(f"Found job: {details['title']}")
        """
        try:
            log.debug("Starting extraction of listing details...")
            
            # Wait for details panel to be present
            log.debug("Waiting for details panel...")
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='contentContainer']"))
                )
                log.debug("Details panel found")
            except TimeoutException as wait_error:
                log.error(f"Timeout waiting for details panel: {str(wait_error)}")
                return None
            
            # Extract each field with detailed logging
            details = {}
            fields = {
                'title': "//div[@id='contentContainer']//h1[@data-automation='jobTitle']",
                'company': "//div[@id='contentContainer']//a[@data-automation='jobCompany']",
                'location': "//div[@id='contentContainer']//span[@data-automation='job-detail-location']",
                'work_type': "//div[@id='contentContainer']//span[@data-automation='job-detail-work-type']",
                'description': "//div[@id='contentContainer']//div[@data-automation='jobDescription']",
                'listing_date': "//div[@id='contentContainer']//span[@data-automation='jobListingDate']"
            }
            
            for field, xpath in fields.items():
                log.debug(f"Attempting to extract {field}...")
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    details[field] = element.text
                    log.debug(f"{field}: {details[field]}")
                except NoSuchElementException:
                    log.error(f"Element not found for {field} with xpath: {xpath}")
                    details[field] = None
            
            # Attempt to extract salary using multiple locators
            salary_locators = [
                "//span[@data-automation='job-detail-add-expected-salary']",
                "//span[@data-automation='job-detail-salary']"
            ]
            
            details['salary'] = None
            for salary_xpath in salary_locators:
                try:
                    element = self.driver.find_element(By.XPATH, salary_xpath)
                    details['salary'] = element.text
                    log.debug(f"Extracted salary: {details['salary']}")
                    break
                except NoSuchElementException:
                    log.debug(f"Salary element not found with xpath: {salary_xpath}")
            
            if not details['salary']:
                log.error("Failed to extract salary information")
            
            details['job_link'] = self.driver.current_url
            log.debug(f"Current URL: {details['job_link']}")
            
            # Validate essential fields
            essential_fields = ['title', 'company', 'description']
            missing_fields = [field for field in essential_fields if not details[field]]
            
            if missing_fields:
                log.error(f"Missing essential fields: {missing_fields}")
                return None
                
            log.debug("Successfully extracted all required details")
            return details
            
        except Exception as e:
            log.error(f"Error extracting listing details: {str(e)}")
            log.error(f"Current URL: {self.driver.current_url}")
            return None
