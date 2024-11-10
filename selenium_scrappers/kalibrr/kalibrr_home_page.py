import json
from selenium.webdriver.common.by import By
from data_handler.file_context import FileContext
from selenium.common.exceptions import NoSuchElementException
import os

# Define the absolute path to the locators directory
LOCATORS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kalibrr_locators.json")

class KalibrrHomePage:
    """
    Represents the Kalibrr home page and provides methods to interact with job listings.

    Attributes:
        driver: The Selenium WebDriver instance used to interact with the web page.
        locators: A dictionary containing locators for various elements on the page.
    """

    def __init__(self, driver, logger):
        """
        Initializes the KalibrrHomePage with a WebDriver and a logger.

        Args:
            driver: The Selenium WebDriver instance.
            logger: The logger instance for logging information.
        """
        global log
        log = logger
        self.driver = driver
        file = FileContext()
        with file.safe_open(LOCATORS_DIR, "r") as json_file:
            self.locators = json.load(json_file)

    def load_more_jobs_button(self):
        """
        Retrieves the locator for the 'Load More Jobs' button.

        Returns:
            str: The locator for the 'Load More Jobs' button.
        """
        return self.locators["LoadMoreJobs"]["locator"]

    def get_job_listing_cards(self):
        """
        Locates job listing cards and returns them as an array of JSON objects.

        Returns:
            list: A list of dictionaries, each representing a job listing with details such as title, company, location, salary, position, job type, job arrangement, and URL.
        """
        locator = self.locators["JobListingCard"]["locator"]
        elements = self.driver.find_elements(By.XPATH, locator)
        job_listings = []
        log.info('Gathering jobs listings')

        for index, element in enumerate(elements, 1):
            log.progress(f'🛰️  Loading {index}/{len(elements)} jobs')
            title = element.find_element(By.XPATH, self.locators["JobTitle"]["locator"])
            company = element.find_element(By.XPATH, self.locators["CompanyName"]["locator"])
            location = element.find_element(By.XPATH, self.locators["Location"]["locator"])
            
            salary_elements = element.find_elements(By.XPATH, self.locators["Salary"]["locator"])
            job_salary = " ".join([salary.text for salary in salary_elements])

            position = element.find_element(By.XPATH, self.locators['JobPosition']['locator'])
            
            job_work_type = element.find_element(By.XPATH, self.locators['WorkType']['locator'])
            try:
                job_work_arrangement = element.find_element(By.XPATH, self.locators['WorkArrangement']['locator'])
                work_arrangement_text = job_work_arrangement.text
            except NoSuchElementException:  
                work_arrangement_text = "unspecified"
            
            job_url = element.find_element(By.XPATH, self.locators['JobLink']['locator']).get_attribute('href')
            
            job_listing = {
                "title": title.text,
                "company": company.text,
                "location": location.text,
                "salary": job_salary,
                "position": position.text,
                "job_type": job_work_type.text,
                "job_arrangement": work_arrangement_text,
                "url": job_url
            }
            job_listings.append(job_listing)

        log.progress_complete('🛰️  All job listings collected')
        return job_listings


