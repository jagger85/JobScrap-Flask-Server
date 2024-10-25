from bright_data_listing_base import BrightDataListingBase
from models.JobListing import JobListing
from csv_parser.csv_handler import write_csv

import json


class IndeedScrapper(BrightDataListingBase):
    def __init__(self, site):
        self.site = site

    # Implement the abstract methods
    def get_job_listings(self):
        print("method not implemented yet")

    def collect_data(self, data):
        job_listing = JobListing(
            site=self.site,
            job_title=self.get_value(data, "job_title"),
            company_name=self.get_value(data, "company_name"),
            job_location=self.get_value(data, "location"),
            job_base_pay_range=self.get_value(data, "salary_formatted"),
            job_posted_date=self.format_date(
                self.get_value(data, "date_posted_parsed")
            ),
            job_employment_type=self.get_value(data, "job_type"),
            url=self.get_value(data, "url"),
        )
        return job_listing


if __name__ == "__main__":
    scrapper = IndeedScrapper("indeed")
    with open("job_listings/indeed_output.json", "r") as file:
        data = json.load(file)

    collected_data = scrapper.collect_data(data)
    write_csv(collected_data)
