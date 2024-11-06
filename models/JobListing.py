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

    def to_dict(self):
        return {
            "site": self.site,
            "listing_date": self.listing_date,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "employment_type": self.employment_type,
            "position": self.position,
            "salary": self.salary,
            "description": self.description,
            "url": self.url
        }
