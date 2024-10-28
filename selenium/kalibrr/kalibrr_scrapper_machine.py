from base_scrap_state_machine import BaseScrapStateMachine
from kalibrr.kalibrr_navigator import KalibrrNavigator
from models.JobListing import JobListing
from typing import List


class KalibrrScrapperMachine(BaseScrapStateMachine):
    def __init__(self, logger, driver):
        global log
        log = logger
        super().__init__(logger)
        self.driver = driver

    def get_job_listings(self):
        """
        Retrieves job listings from Kalibrr.
        """
        log.info("Fetching Kalibrr job listings")
        navigator = KalibrrNavigator(logger=log, driver=self.driver)
        self.listings = navigator.request_listings()

    def process_job_listings(self) -> List[JobListing]:
        """
        Processes the retrieved job listings from Kalibrr.
        """
        log.info("Processing Kalibrr job listings")

        processed_listings = []

        for job in self.listings:
            processed_listing = JobListing(
                site=log.name,
                listing_date=job.get("listing_posted_date", None),
                job_title=job.get("title", None),
                company=job.get("company", None),
                location=job.get("location", None),
                employment_type=f"Type: {job.get('job_type', 'unspecified')} / {job.get('job_arrangement','unspecified')}",
                position=job.get("position", "unspecified"),
                salary=job.get("salary", "unspecified"),
                description=job.get("description", None),
                url=job.get("url", None),
            )
            processed_listings.append(processed_listing)

        return processed_listings

    def process_error(self):
        """
        Handles errors that occur during the scraping process.

        This method should implement specific error handling logic
        for Kalibrr scraping operations.
        """
        log.info("Processing Kalibrr error")
        pass
