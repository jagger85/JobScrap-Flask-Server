from transitions import Machine
from brightdata.brightdata_api import BrightDataClient
from models import LinkedInParams, IndeedParams
from models.JobListing import JobListing
import time
from typing import Union
from config.config import Config
from logger.logger import get_logger
from constants.platforms import Platforms
from constants.platform_states import PlatformStates
from server.state_manager import StateManager
from datetime import datetime

# Define the possible states
states = [
    "idle",
    "requesting_data",
    "waiting_data",
    "processing_data",
    "sending_result",
    "error",
]

# TRANSITIONS
# A transition happens when a trigger is called
# Each transition has a source (current state) and a dest (destination state)
# Error_occurred: Moves the machine to error from any state ('*' represents any state)

transitions = [
    {"trigger": "launch", "source": "*", "dest": "requesting_data"},
    {"trigger": "request_data", "source": "idle", "dest": "requesting_data"},
    {"trigger": "wait_data", "source": "requesting_data", "dest": "waiting_data"},
    {"trigger": "process_data", "source": "waiting_data", "dest": "processing_data"},
    {"trigger": "send_result", "source": "processing_data", "dest": "sending_result"},
    {"trigger": "error_occurred", "source": "*", "dest": "error"},
]


class BrightPioneer:
    def __init__(self,  params: Union[LinkedInParams, IndeedParams]):
        self.state_manager = StateManager()

        global platform_name
        platform_name = params.get_platform_name()
        
        self.params = params
        global platform
        if self.params.__class__.__name__ == 'IndeedParams':
            platform = Platforms.INDEED
        elif self.params.__class__.__name__ == 'LinkedInParams':
            platform = Platforms.LINKEDIN

        global log
        log = get_logger(platform_name)

        global client
        client = BrightDataClient(log)

        self.config = Config()
        self.waiting_time = 60
        self.waiting_retries = 6
        self.waited_times = 0
 
        self.data_manager = self.config.storage
        self.listings = []

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="idle"
        )

    # STATE HANDLERS
    # These methods are automatically called when the machine enters specific states.

    def on_enter_requesting_data(self):
        log.info("Requesting dataset...")
        try:
            response = client.request_snapshot(self.params)
            if response.get("status") == "success":
                self.dataset_id = response.get("dataset_id")
                log.info("Dataset request successful")
                self.wait_data()
            elif response.get("status") == "error":
                error_message = response.get("message", "Unknown error occurred")
                log.error(f"Dataset request failed: {error_message}")
                self.error_occurred(error_message)
            else:
                log.warning(f'Unexpected response status: {response.get("status")}')
                self.error_occurred("Unexpected response from API")
        except Exception as e:
            log.exception("Exception occurred while requesting dataset")
            self.error_occurred(f"Exception during dataset request: {str(e)}")

    def on_enter_waiting_data(self):
        check_interval = 60  # Check every 60 seconds
        waiting_minutes = 0
        log.info(f"Waiting for {platform_name} listings this can take several minutes")

        while True:
            status = client.check_snapshot_status()
            log.debug(status.get("status"))

            if status["status"] == "ready":
                log.info("Data is ready!")
                self.process_data()
                return

            elif status["status"] == "failed":
                self.error_occurred(status["message"])
                return

            elif status["status"] == "running":
                waiting_minutes += check_interval / 60
                log.info(f"Still processing {platform_name}... Waiting time: {int(waiting_minutes)} minutes")

            time.sleep(check_interval)

    def on_enter_processing_data(self):
        log.debug("Processing data...")
        try:
            result = client.retrieve_snapshot()
            if result["status"] == "success":
                log.debug("Dataset retrieved successfully")

                snapshot = result.get("snapshot", [])

                log.debug(f"Retrieved {len(snapshot)} items from the dataset")

                if self.params.__class__.__name__ == 'IndeedParams':
                    processed_listings = self.process_indeed_snapshot(snapshot)
                    self.send_result(processed_listings)
                elif self.params.__class__.__name__ == 'LinkedInParams':
                    processed_listings = self.process_linkedIn_snapshot(snapshot)
                    self.send_result(processed_listings)
            else:
                error_message = result.get("message", "Unknown error occurred")
                log.error(f"Failed to retrieve dataset: {error_message}")
                self.error_occurred(error_message)
        except Exception as e:
            log.exception("Exception occurred while processing data")
            self.error_occurred(f"Exception during data processing: {str(e)}")

    def on_enter_sending_result(self, processed_data):
        log.debug("🎉🎉🎉🎉 we reached the final stage!")
        self.final_listings = processed_data

    def on_enter_error(self, msg):
        self.state_manager.set_platform_state(platform, PlatformStates.ERROR)
        log.error(msg)

    def process_linkedIn_snapshot(self, snapshot):
        log.debug("Processing LinkedIn listings")

        processed_listings = []

        for listing in snapshot:
            processed_listing = JobListing(
                site=self.params.get_platform_name(),
                listing_date=self.parse_date(listing.get('job_posted_date')),
                job_title=listing.get('job_title'),
                company=listing.get('company_name'),
                location=listing.get('job_location'),
                employment_type=listing.get('job_employment_type'),
                position=listing.get('job_seniority_level'),
                salary=listing.get('job_base_pay_range'),
                description=listing.get('job_summary'),
                url=listing.get('url')
            )
            processed_listings.append(processed_listing)

        log.info(f"Received {len(processed_listings)} LinkedIn listings")
        self.send_result(processed_listings)
        return processed_listings

    def parse_date(self, date_str):
        try:
            # Convert ISO format to MM-DD-YY
            if isinstance(date_str, str):
                parsed_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                return parsed_date.strftime('%m-%d-%y')
            return None
        except Exception as e:
            log.error(f"Error parsing date: {e}")
            return None

    def process_indeed_snapshot(self, snapshot):
        log.debug("Processing Indeed listings")

        processed_listings = []

        for listing in snapshot:
            processed_listing = JobListing(
                site=self.params.get_platform_name(),
                listing_date=self.parse_date(listing.get('date_posted_parsed')),
                job_title=listing.get('job_title'),
                company=listing.get('company_name'),
                location=listing.get('location'),
                employment_type=listing.get('job_type'),
                position=None,  # Indeed doesn't provide seniority level
                salary=listing.get('salary_formatted'),
                description=listing.get('description_text'),
                url=listing.get('url')
            )
            processed_listings.append(processed_listing)

        log.info(f"Received {len(processed_listings)} Indeed listings")
        self.send_result(processed_listings)
        return processed_listings

    def start(self):
        try:
            self.final_listings = []
            self.launch()
            return self.final_listings
        
        except Exception as e:
            log.debug(f'An error ocurred {e}')
            log.error('An error has ocurred while processing')
            self.state_manager.set_platform_state(platform, PlatformStates.ERROR)
            self.final_listings = []


if __name__ == "__main__":
    from logger.logger import get_logger

    probe = BrightPioneer(get_logger("LinkedIn"))
