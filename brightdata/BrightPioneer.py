from transitions import Machine
from brightdata.brightdata_api import BrightDataClient
from models import LinkedInParams, IndeedParams
from models import JobListing
import time
from typing import Union

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
    def __init__(self, logger, params: Union[LinkedInParams, IndeedParams], data_manager):
        global log
        global client

        client = BrightDataClient(logger)
        log = logger

        self.waiting_time = 60
        self.waiting_retries = 6
        self.waited_times = 0
        self.params = params
        self.data_manager = data_manager
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
        max_wait_time = 1000  # 4 minutes in seconds
        check_interval = 60  # Check every 30 seconds
        elapsed_time = 0
        log.info("Waiting for data this can take several minutes")

        while elapsed_time < max_wait_time:
            log.info(f"Elapsed time: {elapsed_time} seconds")
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
                log.debug("Still processing")

            time.sleep(check_interval)
            elapsed_time += check_interval

        self.error_occurred("Data retrieval timed out after 1000 seconds")

    def on_enter_processing_data(self):
        log.info("Processing data...")
        try:
            result = client.retrieve_snapshot()
            if result["status"] == "success":
                log.info("Dataset retrieved successfully")

                snapshot = result.get("snapshot", [])
                log.info(f"Retrieved {len(snapshot)} items from the dataset")
                if isinstance(self.params, IndeedParams):
                    processed_listings = self.process_indeed_snapshot(snapshot)
                    # Implement a send result
                elif isinstance(self.params, LinkedInParams):
                    processed_listings = self.process_linkedIn_snapshot(snapshot)
                    # Implement send result
            else:
                error_message = result.get("message", "Unknown error occurred")
                log.error(f"Failed to retrieve dataset: {error_message}")
                self.error_occurred(error_message)
        except Exception as e:
            log.exception("Exception occurred while processing data")
            self.error_occurred(f"Exception during data processing: {str(e)}")

    def on_enter_sending_result(self, processed_data):
        #TODO implement sending to datamanager
        log.info("🎉🎉🎉🎉 we reached the final stage!")

        self.state_result =  "✅ Exploration mission accomplished"

    def on_enter_error(self, msg):
        log.error(msg)
        self.state_result = "🥲 Something bad happened"



    def process_linkedIn_snapshot(self, snapshot):
        log.info("Processing LinkedIn listings")

        processed_listings = []

        for listing in snapshot:
            processed_listing = JobListing(
                site=self.params.get_platform_name(),
                listing_date=listing.get('job_posted_date'),
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

        log.info(f"Processed {len(processed_listings)} LinkedIn listings")
        self.send_result(processed_listings)
        return processed_listings

    def process_indeed_snapshot(self, snapshot):
        log.info("Processing Indeed listings")

        processed_listings = []

        for listing in snapshot:
            processed_listing = JobListing(
                site=self.params.get_platform_name(),
                listing_date=listing.get('date_posted_parsed'),
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

        log.info(f"Processed {len(processed_listings)} Indeed listings")
        self.send_result(processed_listings)
        return processed_listings



if __name__ == "__main__":
    from logger.logger import get_logger

    probe = BrightPioneer(get_logger("LinkedIn"))
