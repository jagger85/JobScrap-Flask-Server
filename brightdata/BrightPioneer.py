from transitions import Machine
from brightdata.brightdata_api import BrightDataClient
from models import LinkedInParams, IndeedParams
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
    {"trigger": "init", "source": "*", "dest": "requesting_data"},
    {"trigger": "request_data", "source": "idle", "dest": "requesting_data"},
    {"trigger": "wait_data", "source": "requesting_data", "dest": "waiting_data"},
    {"trigger": "process_data", "source": "waiting_data", "dest": "processing_data"},
    {"trigger": "send_result", "source": "processing_data", "dest": "sending_result"},
    {"trigger": "error_occurred", "source": "*", "dest": "error"},
]


class BrightPioneer:
    def __init__(self, logger, params: Union[LinkedInParams, IndeedParams]):  # type: ignore
        global log
        global client

        client = BrightDataClient()
        log = logger

        self.waiting_time = 60
        self.waiting_retries = 6
        self.waited_times = 0
        self.params = params

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="idle"
        )
        self.init()

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

            elif status["status"] == "error":
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

                # log the number of items retrieved
                data = result.get("data", [])
                log.info(f"Retrieved {len(data)} items from the dataset")
                self.send_result()
            else:
                error_message = result.get("message", "Unknown error occurred")
                log.error(f"Failed to retrieve dataset: {error_message}")
                self.error_occurred(error_message)
        except Exception as e:
            log.exception("Exception occurred while processing data")
            self.error_occurred(f"Exception during data processing: {str(e)}")

    def on_enter_sending_result(self):
        log.info("🎉🎉🎉🎉 we reached the final stage!")

    def on_enter_error(self, msg):
        log.error(msg)


if __name__ == "__main__":
    from logger import linkedin_logger

    probe = BrightPioneer(linkedin_logger)
