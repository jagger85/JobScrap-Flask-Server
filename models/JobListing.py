from dataclasses import dataclass


@dataclass
class JobListing:
    site: str
    listing_date: str
    job_title: str
    company: str
    location: str
    employment_type: str
    position: str
    salary: str
    description: str
    url: str
