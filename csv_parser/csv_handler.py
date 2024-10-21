import csv
import os
from models.JobListing import JobListing

# Define the headers for the CSV file
HEADERS = [
    'site', 'job_title', 'company_name', 'job_location',
    'job_base_pay_range', 'job_posted_date', 'job_employment_type', 'url'
]

def write_csv(job_listing: JobListing):
    """
    Writes a JobListing object to a CSV file.

    :param job_listing: An instance of JobListing containing job details.
    :raises ValueError: If PYTHONPATH is not set.
    """
    # Get the root directory from PYTHONPATH
    root_dir = os.environ.get('PYTHONPATH', '')
    
    if not root_dir:
        raise ValueError("PYTHONPATH is not set. Please set it to the root directory of your project.")
    
    # Create the full file path
    file_name = f'{job_listing.site}_jobs.csv'
    full_file_path = os.path.join(root_dir, 'outputs', file_name)
    
    print(f"Writing to {full_file_path}")
    
    # Open the CSV file and write the job listing
    with open(full_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerow(job_listing.__dict__)
