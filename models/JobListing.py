from dataclasses import dataclass


@dataclass
class JobListing:
    site: str
    job_title: str
    company_name: str
    job_location: str
    job_base_pay_range: str
    job_posted_date: str
    job_employment_type: str
    url: str
