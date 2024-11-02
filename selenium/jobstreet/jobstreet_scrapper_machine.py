from base_scrap_state_machine import BaseScrapStateMachine
from jobstreet.jobstreet_navigator import JobstreetNavigator
from typing import List
from models.JobListing import JobListing
from datetime import datetime, timedelta
import re
from config import Config
from models.date_range import DateRange

class JobstreetScrapperMachine(BaseScrapStateMachine):
    def __init__(self, logger):
        global log
        log = logger
        super().__init__(logger)
        
        self.driver.get(self.build_jobstreet_url())

    def build_jobstreet_url(self) -> str:
        """
        Constructs the Jobstreet URL with the appropriate date range parameter.
        """
        date_range_mapping = {
            DateRange.PAST_24_HOURS: "1",
            DateRange.PAST_WEEK: "7",
            DateRange.PAST_15_DAYS: "15",
            DateRange.PAST_MONTH: "31"
        }
        
        base_url = Config().jobstreet_url
        date_range_value = date_range_mapping.get(self.date_range)
        classification = '6263%2C6281'
        subclassification = '6268%2C6273%2C6284%2C6286%2C6287%2C6290%2C6302'
        log.debug(f"Jobstreet scrapped url: {base_url}?classification={classification}&daterange={date_range_value}&subclassification={subclassification}")
        
        return f"{base_url}?classification={classification}&daterange={date_range_value}&subclassification={subclassification}"

    def get_job_listings(self):
        """
        Retrieves listing listings from Jobstreet.
        """
        log.info("Fetching Jobstreet listings")
        navigator = JobstreetNavigator(logger=log, driver=self.driver)
        self.listings = navigator.request_listings()

    def process_job_listings(self) -> List[JobListing]:
        log.info("Processing Jobstreet listings")

        processed_listings = []

        for listing in self.listings:
            processed_listing = JobListing(
                site=log.name,
                listing_date=convert_relative_dates_to_absolute(listing.get("listing_date", None)),
                job_title=listing.get("title", None),
                company=listing.get("company", None),
                location=listing.get("location", None),
                employment_type=listing.get("work_type", "unspecified"),
                position=listing.get("position", "unspecified"),
                salary=listing.get("salary", "unspecified"),
                description=listing.get("description", None),
                url=listing.get("job_link", None),
            )
            processed_listings.append(processed_listing)

        return processed_listings

    def process_error(self):
        log.error("❌  Error occurred")
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
