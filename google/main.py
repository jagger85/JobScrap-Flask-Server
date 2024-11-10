from google.cloud import talent
from google.oauth2 import service_account
import os

def search_computer_it_jobs_in_philippines():
    # Initialize the client with the service account credentials
    credentials = service_account.Credentials.from_service_account_file(
        './jobsweepGoogle.json'
    )
    client = talent.JobServiceClient(credentials=credentials)

    # Define the parent resource using the default tenant
    parent = "projects/jobsweep-441107"

    # Define the location filter for the Philippines
    location_filter = talent.LocationFilter(
        region_code='PH'
    )

    # Define the job category filter for COMPUTER_AND_IT
    job_category_filter = talent.JobCategory.COMPUTER_AND_IT

    # Create the job query
    job_query = talent.JobQuery(
        location_filters=[location_filter],
        job_categories=[job_category_filter]
    )

    # Create the request metadata
    request_metadata = talent.RequestMetadata(
     allow_missing_ids= True
    )

    # Create the search jobs request
    request = talent.SearchJobsRequest(
        parent=parent,
        request_metadata=request_metadata,
        job_query=job_query
    )

    # Execute the search
    response = client.search_jobs(request=request)
    print(response)
    # Process the response
    for matching_job in response.matching_jobs:
        print(f"Job title: {matching_job.job.title}")
        print(f"Job summary: {matching_job.job_summary}")
        print(f"Job location: {matching_job.job.addresses}")



if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "jobsweepGoogle.json"
  
    search_computer_it_jobs_in_philippines()
 