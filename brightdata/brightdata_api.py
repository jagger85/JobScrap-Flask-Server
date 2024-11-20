import requests
import os
from models.IndeedParams import IndeedParams
from models.LinkedInParams import LinkedInParams
from dotenv import load_dotenv


class BrightDataClient:
    """
    A client for interacting with the Bright Data API.

    This class provides methods to request, check the status of, and retrieve snapshots
    from the Bright Data API. It handles authentication and API communication details.

    Attributes:
        snapshot_id (str): The ID of the current snapshot being processed.
        headers (dict): HTTP headers used for API requests, including authentication.

    Methods:
        request_snapshot(params): Initiates a new snapshot scraping request.
        check_snapshot_status(): Checks the status of the current snapshot.
        retrieve_snapshot(): Retrieves the data for the current snapshot.

    Usage:
        >>> client = BrightDataClient()
        >>> params = LinkedInParams(keyword="software engineer", location="New York")
        >>> client.request_snapshot(params)
        >>> status = client.check_snapshot_status()
        >>> if status['status'] == 'ready':
        ...     data = client.retrieve_snapshot()
    """

    def __init__(self, logger):
        global log
        log = logger

        load_dotenv()
        API_KEY = os.getenv("BRIGHT")

        global BASE_URL
        BASE_URL = "https://api.brightdata.com/datasets/v3"
        self.snapshot_id = None
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

    # CALLS
    # Request the platform to scrap and create a snapshot
    def request_snapshot(self, params: LinkedInParams | IndeedParams):
        """
        Request the platform to scrape and create a snapshot.

        This method sends a POST request to the Bright Data API to initiate
        the scraping process and create a snapshot based on the provided parameters.

        This method sends a POST request to the Bright Data API to initiate
        the scraping process and create a dataset based on the provided parameters.

        Args:
            params (LinkedInParams | IndeedParams): An object containing the parameters
                for the snapshot request. Must be an instance of either LinkedInParams
                or IndeedParams.

        Returns:
            dict: A dictionary containing status information. Possible keys are:
                - 'status': A string indicating the request status ('success' or 'error').
                - 'message': A string providing additional information about the status.
                - 'snapshot_id': The ID of the created snapshot (only present if status is 'success').

        Raises:
            None: This method handles all exceptions internally and returns
            error information in the result dictionary.

        Example:
            >>> client = BrightDataClient()
            >>> linkedin_params = LinkedInParams(keyword="software engineer", location="New York")
            >>> result = client.request_snapshot(linkedin_params)
            >>> print(result)
            {'status': 'success', 'message': 'snapshot request successful', 'snapshot_id': 'abc123'}
        """

        URL = f"{BASE_URL}/trigger/?dataset_id={params.get_dataset_id()}&type=discover_new&discover_by=keyword"
        log.debug(f"Requested dataset id: {params.get_dataset_id()}")
        log.debug(f"Requested dataset {URL}")

        payload = [params.to_dict()]
        print(payload)
        log.debug(f"Query params: {payload}")

        log.debug(f"Query params: {payload}")

        try:
            response = requests.post(
                URL, headers=self.headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data = response.json()
            self.snapshot_id = data.get("snapshot_id")

            if not self.snapshot_id:
                return {
                    "status": "error",
                    "message": "snapshot ID not received in the response",
                }

            return {
                "status": "success",
                "message": "snapshot request successful",
                "snapshot_id": self.snapshot_id,
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to connect to the API: {str(e)}",
            }
        except ValueError as e:
            return {"status": "error", "message": f"Error processing request: {str(e)}"}
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
            }

    # Request if the snapshot is ready
    def check_snapshot_status(self):
        """
        Check the status of a snapshot.

        This method queries the API to determine the current status of a snapshot
        identified by the given snapshot_id.

        Returns:
            dict: A dictionary containing status information. Possible keys are:
                - 'status': A string indicating the snapshot status
                  ('ready', 'running', 'failed', 'unknown', or 'error').
                - 'message': A string providing additional information about the status.

        Raises:
            None: This method handles all exceptions internally and returns
            error information in the result dictionary.

        Example:
            >>> client = BrightDataClient()
            >>> result = client.check_snapshot_status("snapshot123")
            >>> print(result)
            {'status': 'ready', 'message': 'snapshot is ready for retrieval'}
        """
        URL = f"{BASE_URL}/progress/{self.snapshot_id}"
        log.debug(f"Snapshot id: {self.snapshot_id}")
        log.debug(f"Snapshot requested url: {URL}")

        try:
            response = requests.get(URL, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            status = data.get("status")

            if status == "ready":
                return {"status": "ready", "message": "Snapshot is ready for retrieval"}
            elif status == "running":
                return {
                    "status": "running",
                    "message": "Snapshot is still being processed",
                }
            elif status == "failed":
                error_message = data.get("error_message")
                return {
                    "status": "failed",
                    "message": f"Brightdata failed: {error_message}",
                }
            else:
                return {"status": "unknown", "message": f"Unknown status: {status}"}

        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            return {
                "status": "error",
                "message": f"Failed to connect to the API: {str(e)}",
            }
        except ValueError as e:
            # Handle JSON decoding errors
            return {
                "status": "error",
                "message": f"Error processing API response: {str(e)}",
            }
        except Exception as e:
            # Catch any other unexpected errors
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
            }

    # Request the snapshot
    def retrieve_snapshot(self, snapshot_id=None):
        """
        Retrieve the snapshot from the Bright Data API.

        This method sends a GET request to the Bright Data API to retrieve
        the snapshot identified by the given snapshot_id or the current snapshot_id.

        Args:
            snapshot_id (str, optional): The ID of the snapshot to retrieve.
                If not provided, uses the current snapshot_id.

        Returns:
            dict: A dictionary containing status information and the snapshot. Possible keys are:
                - 'status': A string indicating the retrieval status ('success' or 'error').
                - 'message': A string providing additional information about the status.
                - 'data': The retrieved snapshot (only present if status is 'success').

        Raises:
            None: This method handles all exceptions internally and returns
            error information in the result dictionary.

        Example:
            >>> client = BrightDataClient()
            >>> result = client.retrieve_snapshot("snapshot123")
            >>> print(result)
            {'status': 'success', 'message': 'Snapshot retrieved successfully', 'data': {...}}
        """
        # Use the provided snapshot_id if given, otherwise use the current snapshot_id
        snapshot_id = snapshot_id or self.snapshot_id

        if not snapshot_id:
            return {"status": "error", "message": "No snapshot ID provided or set"}

        URL = f"{BASE_URL}/snapshot/{snapshot_id}"

        params = {
            "format": "json",
        }
        try:
            response = requests.get(
                URL, headers=self.headers, params=params, timeout=60
            )
            response.raise_for_status()

            snapshot = response.json()

            return {
                "status": "success",
                "message": "Snapshot retrieved successfully",
                "snapshot": snapshot
            }
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            return {
                "status": "error",
                "message": f"Failed to connect to the API: {str(e)}",
            }
        except ValueError as e:
            # Handle JSON decoding errors
            return {
                "status": "error",
                "message": f"Error processing API response: {str(e)}",
            }
        except Exception as e:
            # Catch any other unexpected errors
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
            }

    # Request a list of snapshots requested for a specific dataset
    def retrieve_snapshots_list(self, dataset_id):
        """
        Retrieve a list of snapshots for a specific dataset.

        This method sends a GET request to the Bright Data API to retrieve
        a list of snapshots associated with the given dataset_id.

        Args:
            dataset_id (str): The ID of the dataset for which to retrieve snapshots.

        Returns:
            dict: A dictionary containing status information and the snapshots list. Possible keys are:
                - 'status': A string indicating the retrieval status ('success' or 'error').
                - 'message': A string providing additional information about the status.
                - 'data': The list of snapshots (only present if status is 'success').

        Raises:
            None: This method handles all exceptions internally and returns
            error information in the result dictionary.

        Example:
            >>> client = BrightDataClient()
            >>> result = client.retrieve_snapshots_list("dataset123")
            >>> print(result)
            {'status': 'success', 'message': 'Snapshots list retrieved successfully', 'data': [...]}
        """
        URL = f"{BASE_URL}/snapshots"
        params = {
            "dataset_id": dataset_id
            # TODO
            # "from_date" - List only snapshots that were created after a specific date, Example: from_date=2024-01-01
            # "to_date" - List only snapshots that were created before a specific date, Example: from_date=2024-04-01
        }

        try:
            response = requests.get(
                URL, headers=self.headers, params=params, timeout=60
            )
            response.raise_for_status()

            snapshots_list = response.json()

            return {
                "status": "success",
                "message": "Snapshots list retrieved successfully",
                "data": snapshots_list,
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to connect to the API: {str(e)}",
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Error processing API response: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
            }


if __name__ == "__main__":
    client = BrightDataClient()
