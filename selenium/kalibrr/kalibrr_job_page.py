import json
from selenium.webdriver.common.by import By
from file_handler.file_context import FileContext
from datetime import datetime

class KalibrrJobPage():
    def __init__(self,driver):
        self.driver = driver
        file = FileContext()
        with file.safe_open("selenium/kalibrr/kalibrr_locators.json", "r") as json_file:
            self.locators = json.load(json_file)

    def get_job_description(self):
        """
        Retrieve the job description from the job page.

        This method locates the job description element on the page and extracts
        the text content. It handles both list and paragraph formats.

        Returns:
            str: The job description text.

        Example:
            >>> job_page = KalibrrJobPage(driver)
            >>> description = job_page.get_job_description()
            >>> print(description)
        """
        # Locate the description element
        description_element = self.driver.find_element(By.XPATH, self.locators["JobDescription"]["locator"])
        
        # Try to find list items within the description
        list_items = description_element.find_elements(By.TAG_NAME, "li")
        
        if list_items:
            # Extract text from each list item and join them into a single string
            description_text = "\n".join([item.text for item in list_items])
        else:
            # If no list items, extract text from paragraph elements
            paragraphs = description_element.find_elements(By.TAG_NAME, "p")
            description_text = "\n".join([para.text for para in paragraphs])
        
        return description_text
        
    def get_job_listing_date(self):
        """
        Retrieve the job listing date from the job page.

        This method locates the job listing date element on the page and extracts
        the text content, converting it from ISO format to MM-DD-YY format.

        Returns:
            str: The job listing date in MM-DD-YY format.

        Example:
            >>> job_page = KalibrrJobPage(driver)
            >>> listing_date = job_page.get_job_listing_date()
            >>> print(listing_date)  # Output: 10-18-24
        """
        date_posted_element = self.driver.find_element(By.XPATH, self.locators["DatePosted"]["locator"])
        iso_date = date_posted_element.get_attribute("innerHTML")
        
        # Convert ISO date to datetime and format as MM-DD-YY
        date_obj = datetime.fromisoformat(iso_date.split('+')[0])
        formatted_date = date_obj.strftime('%m-%d-%y')
        
        return formatted_date

    def get_valid_through(self):
        """
        Retrieve the valid through date from the job page.

        This method locates the valid through date element on the page and extracts
        the text content. It handles the application deadline information.

        Returns:
            str: The valid through date text.

        Example:
            >>> job_page = KalibrrJobPage(driver)
            >>> valid_through = job_page.get_valid_through()
            >>> print(valid_through)
        """
        valid_through_element = self.driver.find_element(By.XPATH, self.locators["ValidThrough"]["locator"])
        return valid_through_element.get_attribute("innerHTML")
