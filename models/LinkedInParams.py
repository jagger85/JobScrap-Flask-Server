from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

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
    ASSOCIATE = "Asociate"
    MID_SENIOR_LEVEL = "Mid-Senior level"
    DIRECTOR = "Director"

class Remote(Enum):
    ON_SITE = "On-site"
    REMOTE = "Remote"
    HYBRID = "Hybrid"

@dataclass
class LinkedInParams:

    location: str
    keywords: List[str]
    country: str
    time_range: Optional[TimeRange] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    remote: Optional[Remote] = None
    company: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "location": self.location,
            "keyword": ', '.join(self.keywords),
            "country": self.country,
            "time_range": self.time_range.value if self.time_range else "",
            "job_type": self.job_type.value if self.job_type else "",
            "experience_level": self.experience_level.value if self.experience_level else "",
            "remote": self.remote.value if self.remote else "",
            "company": self.company if self.company else ""
        }
##Original
##{"location":"New York","keyword":"data analyst","country":"US","time_range":"Past 24 hours","job_type":"Part-time","experience_level":"Entry level","remote":"Remote","company":""}
##Personal
##{'location': 'New York', 'keyword': 'data analyst', 'country': 'US', 'time_range': 'Past 24 hours', 'job_type': 'Part-time', 'experience_level': 'Entry level', 'remote': 'Remote', 'company': ''}

    def __post_init__(self):
        if self.time_range and not isinstance(self.time_range, TimeRange):
            raise ValueError(f"time_range must be an instance of TimeRange Enum, got {type(self.time_range)}")
        if self.job_type and not isinstance(self.job_type, JobType):
            raise ValueError(f"job_type must be an instance of JobType Enum, got {type(self.job_type)}")
        if self.experience_level and not isinstance(self.experience_level, ExperienceLevel):
            raise ValueError(f"experience_level must be an instance of ExperienceLevel Enum, got {type(self.experience_level)}")
        if self.remote and not isinstance(self.remote, Remote):
            raise ValueError(f"remote must be an instance of Remote Enum, got {type(self.remote)}")
