import csv
import os
from models.JobListing import JobListing
from logger import get_logger
from datetime import datetime
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


def write_csv(job_listing: JobListing):
    """
    Writes a JobListing object to a CSV file.

    :param job_listing: An instance of JobListing containing job details.
    :raises ValueError: If PYTHONPATH is not set.
    """
    # Get the root directory from PYTHONPATH
    root_dir = os.environ.get("PYTHONPATH", "")

    if not root_dir:
        raise ValueError(
            "PYTHONPATH is not set. Please set it to the root directory of your project."
        )

    # Create the full file path
    file_name = f"{job_listing.site}_jobs.csv"
    full_file_path = os.path.join(root_dir, "outputs", file_name)

    print(f"Writing to {full_file_path}")

    # Open the CSV file and write the job listing
    with open(full_file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerow(job_listing.__dict__)


def write_csv_multiple(job_listings: list[JobListing]):
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
        >>> write_csv_multiple(listings)
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

    log.info("📡  Received data")

    # Open the CSV file and write the job listings
    with open(full_file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
        writer.writeheader()
        for job_listing in job_listings:
            writer.writerow(job_listing.__dict__)
    log.info(f"📥  Wrote to {full_file_path}")
