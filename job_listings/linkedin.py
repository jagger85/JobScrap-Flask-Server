import json
from bright_data_listing_base import BrightDataListingBase
from models.JobListing import JobListing
from csv_parser.csv_handler import write_csv
from models.LinkedInParams import *
from bright_link_call import request_dataset_id

class LinkedinScrapper(BrightDataListingBase):

    def __init__(self):
        self.site = 'LinkedIn'

    # Implement the abstract methods
    def get_job_listings(self,params):
        print(params)

    def collect_data(self,data):
        job_listing = JobListing(
            site=self.site,
            job_title=self.get_value(data, 'job_title'),
            company_name=self.get_value(data, 'company_name'),
            job_location=self.get_value(data, 'job_location'),
            job_base_pay_range=self.get_value(data, 'job_base_pay_range'),
            job_posted_date=self.format_date(self.get_value(data, 'job_posted_date')),
            job_employment_type=self.get_value(data['discovery_input'], 'keyword'),
            url=self.get_value(data, 'url')
        )
        return job_listing

if __name__ == '__main__':
    scrapper = LinkedinScrapper()

    params = LinkedInParams(
        location="New York",
        keywords=["data analyst"],
        country="US",
        time_range= TimeRange.PAST_24_HOURS,
        job_type= JobType.PART_TIME,
        experience_level= ExperienceLevel.ENTRY_LEVEL,
        remote= Remote.REMOTE,
    )
    request_dataset_id(params)

    # with open('job_listings/linkedin_output.json', 'r') as file:
    #     data = json.load(file)
    
    # collected_data = scrapper.collect_data(data)
    # write_csv(collected_data)