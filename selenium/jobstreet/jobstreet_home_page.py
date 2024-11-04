import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from data_handler.file_context import FileContext

class JobstreetHomePage:
    def __init__(self, driver, logger):
        global log
        log = logger
        self.driver = driver
        file = FileContext()
        with file.safe_open("jobstreet/jobstreet_locators.json", "r") as json_file:
            self.locators = json.load(json_file)
        
    def get_listings_cards_id(self):
        """Get all job listing IDs from current page"""
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
                        log.progress(f"Extracted listing ID: {listing_id}")
                        listing_ids.append(listing_id)
                    else:
                        log.error("\nCould not find data-job-id attribute")
                        
                except NoSuchElementException as e:
                    log.error(f"Error extracting data from card: {str(e)}")
                    continue
            log.progress_complete("Extracted listings complete")
            return listing_ids
            
        except TimeoutException:
            log.error("Timeout waiting for job cards to load")
            return []

    def go_to_next_page(self):
        """Navigate to next page if available"""
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
        """Extract all required listing details from the current view"""
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
