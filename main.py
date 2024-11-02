from brightdata.BrightPioneer import BrightPioneer
from models.LinkedInParams import LinkedInParams, TimeRange
from models.IndeedParams import IndeedParams
from logger.logger import get_logger, set_log_level
import logging
if __name__ == "__main__":
    set_log_level(logging.DEBUG)
    linkedin_params = LinkedInParams(
        location="Cebu", keywords="Angular", time_range=TimeRange.PAST_MONTH
    )
    indeed_params = IndeedParams(location="Manila", keywords="angular")

    pioneer = BrightPioneer(get_logger("LinkedIn"), indeed_params).launch()
