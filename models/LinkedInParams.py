from dataclasses import dataclass, field
from typing import Dict
from enum import Enum
from constants.date_range import DateRange
from logger.logger import get_logger

dataset_id = "gd_lpfll7v5hcqtkxl6l"
platform_name = "LinkedIn"

class TimeRange(Enum):
    PAST_24_HOURS = "Past 24 hours"
    PAST_WEEK = "Past week"
    PAST_MONTH = "Past month"
    ANY_TIME = "Any time"


class JobType(Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    VOLUNTEER = "Volunteer"


class ExperienceLevel(Enum):
    INTERNSHIP = "Internship"
    ENTRY_LEVEL = "Entry level"
    ASSOCIATE = "Associate"
    MID_SENIOR_LEVEL = "Mid-Senior level"
    DIRECTOR = "Director"


class Remote(Enum):
    ON_SITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"


@dataclass(frozen=True)
class LinkedInParams:
    """
    A class to represent LinkedIn job search parameters.

    Attributes:
        location ([str]): The location to search for jobs.
        keywords ([str]): The keywords to use in the job search.
        date_range (Optional[TimeRange]): The time range for job postings.
        job_type (Optional[JobType]): The type of job (e.g., full-time, part-time).
        experience_level (Optional[ExperienceLevel]): The required experience level.
        remote (Optional[Remote]): The work arrangement (e.g., on-site, remote).
        company (Optional[str]): The company name to filter job postings.
        country (str): The country code for the job search (default is "PH").
    """
    
    location: str = field(default="philippines", init=False)
    keywords: str = field(default="software development", init=False)
    country: str = field(default="PH", init=False)
    date_range : DateRange 

    def __post_init__(self):
        log = get_logger("LinkedIn")
        
        if not isinstance(self.location, str) or not self.location.strip():
            log.warning("Location is empty")
            raise

        if not isinstance(self.keywords, str) or not self.keywords.strip():
            log.warning("Keywords are empty")
            raise
        
        if self.date_range == DateRange.PAST_15_DAYS:
            log.warning('LinkedIn does not provide 2 weeks, searching for last week instead')
            #TODO LinkedIn does not provide past 15 days
            self.date_range == DateRange.PAST_WEEK
            pass
        
        # if self.job_type and not isinstance(self.job_type, JobType):
        #     log.warning(
        #         f"job_type must be an instance of JobType Enum, got {type(self.job_type)}"
        #     )
        # if self.experience_level and not isinstance(self.experience_level, ExperienceLevel):
        #     log.warning(
        #         f"experience_level must be an instance of ExperienceLevel Enum, got {type(self.experience_level)}"
        #     )
        # if self.remote and not isinstance(self.remote, Remote):
        #     log.warning(
        #         f"remote must be an instance of Remote Enum, got {type(self.remote)}"
        #     )

    def to_dict(self) -> Dict:
        return {
            "location": self.location,
            "keyword": self.keywords,
            "country": self.country,
            "date_range": self.date_range.value,
        }
    


    def get_dataset_id(self):
        """

        Returns:
            str: The unique identifier for the BrightData dataset.
        """
        return dataset_id
    
    def get_platform_name(self):
        """

        Returns:
            str: The platform name.
        """
        return platform_name
    
    def __dict__(self):
        return self.to_dict()
