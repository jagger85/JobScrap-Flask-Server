from brightdata.BrightPioneer import BrightPioneer
from models.LinkedInParams import LinkedInParams, TimeRange
from models.IndeedParams import IndeedParams
from logger import get_logger

if __name__ == "__main__":
    linkedin_params = LinkedInParams(
        location="Cebu", keywords="React", time_range=TimeRange.PAST_WEEK
    )

    indeed_params = IndeedParams(location="Manila", keywords="React")

    pioneer = BrightPioneer(get_logger("LinkedIn"), linkedin_params)
