import json
from selenium.webdriver.common.by import By
from file_handler.file_context import FileContext
from selenium.common.exceptions import NoSuchElementException


class KalibrrHomePage:
    def __init__(self, driver, logger):
        global log
        log = logger
        self.driver = driver
        file = FileContext()
        with file.safe_open("selenium/kalibrr/kalibrr_locators.json", "r") as json_file:
            self.locators = json.load(json_file)


    def load_more_jobs_button(self):
        return self.locators["LoadMoreJobs"]["locator"]

    def get_job_listing_cards(self):
        """
        Function to locate job listing cards and return them as an array of JSON objects.
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

    def get_job_listing_card_css(self):
        """
        Function to locate job listing cards using the JobListingCardCSS locator.
        """
        locator = self.locators["JobListingCardCSS"]["locator"]
        elements = self.driver.find_elements(By.CSS_SELECTOR, locator)
        for element in elements:
            print(element.text)

            # job_listing_date = element.find_element(By.XPATH, self.locators['ListingDate']['locator'])
            # job_description = element.find_element(By.XPATH, self.locators['']['locator'])

