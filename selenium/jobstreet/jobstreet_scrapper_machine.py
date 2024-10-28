from base_scrap_state_machine import BaseScrapStateMachine
from jobstreet.jobstreet_navigator import JobstreetNavigator
from typing import List
from models.JobListing import JobListing
from datetime import datetime, timedelta
import re


class JobstreetScrapperMachine(BaseScrapStateMachine):
    def __init__(self, logger, driver):
        global log
        log = logger
        super().__init__(logger)
        self.driver = driver

    def get_job_listings(self):
        """
        Retrieves job listings from Jobstreet.
        """
        log.info("Fetching Jobstreet listings")
        navigator = JobstreetNavigator(logger=log, driver=self.driver)
        self.listings = navigator.request_listings()
        

    def process_job_listings(self) -> List[JobListing]:
        log.info("Processing Jobstreet listings")

        processed_listings = []

        for job in self.listings:
            processed_listing = JobListing(
                site=log.name,
                listing_date=convert_relative_dates_to_absolute(job.get("listing_date", None)),
                job_title=job.get("title", None),
                company=job.get("company", None),
                location=job.get("location", None),
                employment_type=job.get("work_type", "unspecified"),
                position=job.get("position", "unspecified"),
                salary=job.get("salary", "unspecified"),
                description=job.get("description", None),
                url=job.get("job_link", None),
            )
            processed_listings.append(processed_listing)


        return processed_listings

    def process_error(self):
        log.error("❌  Error ocurred")
        pass


def convert_relative_dates_to_absolute(date_str):
    """
    Converts a relative listing date to an absolute date in MM-DD-YY format.

    Args:
        date_str (str): A string representing a relative date.

    Returns:
        str: A string representing the absolute date in MM-DD-YY format.
    """
    now = datetime.now()
    match = re.match(r"Posted (\d+)([hd]) ago", date_str)
    if match:
        value, unit = match.groups()
        value = int(value)

        if unit == 'h':  # hours
            date = now - timedelta(hours=value)
        elif unit == 'd':  # days
            date = now - timedelta(days=value)

        return date.strftime("%m-%d-%y")
    
    return None  # or raise an exception if the format is not matched
