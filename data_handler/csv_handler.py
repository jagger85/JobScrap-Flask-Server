import csv
import os
from models.JobListing import JobListing
from logger.logger import get_logger
from datetime import datetime
from data_handler.base_data_handler import BaseDataHandler
import json
# Define the headers for the CSV file

global log
log = get_logger('CSV_parser')
HEADERS = [
    "site",
    "listing_date",
    "job_title",
    "company",
    "location",
    "employment_type",
    "position",    
    "salary",
    "description",
    "url",
]


class CsvHandler(BaseDataHandler):
    
    def store_snapshot(self,job_listings: list[JobListing]):
        """
        Writes multiple JobListing objects to a CSV file.

        Args:
            job_listings (list[JobListing]): A list of JobListing instances containing job details.

        Raises:
            ValueError: If PYTHONPATH is not set or if the job_listings list is empty.

        Returns:
            None: This method doesn't return anything, it writes data to a CSV file.

        Example:
            >>> listings = [JobListing(...), JobListing(...)]
            >>> store_snapshot(listings)
        """
        if not job_listings:
            raise ValueError("The job_listings list is empty.")

        # Get the root directory from PYTHONPATH
        root_dir = os.environ.get("PYTHONPATH", "")

        if not root_dir:
            raise ValueError(
                "PYTHONPATH is not set. Please set it to the root directory of your project."
            )

        # Get the current date and time
        current_time = datetime.now().strftime("%m-%d-%y_%Hh-%Mm")

        # Create the file name with the date and time
        file_name = f"{job_listings[0].site}_jobs_{current_time}.csv"
        full_file_path = os.path.join(root_dir, "output", file_name)

        log.debug("📡  Received data")

        # Open the CSV file and write the job listings
        with open(full_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
            writer.writeheader()
            for job_listing in job_listings:
                writer.writerow(job_listing.__dict__)
        log.debug(f"📥  Wrote to {full_file_path}")
    
    def store_snapshot_list(self, dataset_id: str, snapshot_list: json):
        """
        Stores a snapshot list with status information in a CSV file.

        Args:
            dataset_id (str): The unique identifier for the dataset
            snapshot_list (json): The JSON data containing the snapshot list status information

        Returns:
            str: Path to the created CSV file

        Raises:
            ValueError: If PYTHONPATH is not set or if the snapshot_list is empty
        """
        if not snapshot_list or 'data' not in snapshot_list:
            raise ValueError("The snapshot list is empty or invalid format.")

        root_dir = os.environ.get("PYTHONPATH", "")
        if not root_dir:
            raise ValueError("PYTHONPATH is not set. Please set it to the root directory of your project.")

        current_time = datetime.now().strftime("%m-%d-%y_%Hh-%Mm")
        file_name = f"snapshot_status_{dataset_id}_{current_time}.csv"
        full_file_path = os.path.join(root_dir, "output", file_name)

        log.info(f"📡  Processing snapshot list for dataset {dataset_id}")

        # Define headers for snapshot status CSV
        status_headers = ['snapshot_id', 'dataset_id', 'status', 'dataset_size', 'created']

        with open(full_file_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=status_headers)
            writer.writeheader()
            
            for snapshot in snapshot_list['data']:
                row = {
                    'snapshot_id': snapshot.get('id', ''),
                    'dataset_id': snapshot.get('dataset_id', ''),
                    'status': snapshot.get('status', ''),
                    'dataset_size': snapshot.get('dataset_size', 0),
                    'created': snapshot.get('created', '')
                }
                writer.writerow(row)

        log.debug(f"📥  Wrote snapshot status list for dataset {dataset_id} to {full_file_path}")
        return full_file_path
    
    def get_snapshot(self):
        log.warning("Method get snapshot not implemented yet")
        pass
    
    def get_snapshot_list(list):
        log.warning("Method get snapshot list not implement yet")
        pass
    