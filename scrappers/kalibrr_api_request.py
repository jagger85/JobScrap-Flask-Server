from datetime import datetime, timezone, timedelta
import requests
from constants import DateRange
from models.JobListing import JobListing
from logger.logger import get_logger
from bs4 import BeautifulSoup

class KalibrrAPIClient:
    """
    Client for interacting with Kalibrr's job listing API.

    This class manages API requests to Kalibrr's job board, including date range
    filtering and response processing.

    Args:
        date_range (DateRange, optional): Time period for which to collect job listings.
            Defaults to None for all available listings.

    Attributes:
        log (Logger): Logger instance for operation tracking.
        base_url (str): Base URL for Kalibrr's job board API.
        date_range (DateRange): Selected time period for job listings.
        state_manager (StateManager): Manages the scraping operation state.
        start_date (datetime): Start of the date range filter.
        end_date (datetime): End of the date range filter.

    Example:
        >>> from constants.date_range import DateRange
        >>> client = KalibrrAPIClient(DateRange.PAST_WEEK)
        >>> listings = client.start()
    """

    def __init__(self, days: str, keywords: str = None):
        self.days = int(days)
        self.log = get_logger("Kalibrr")
        self.base_url = "https://www.kalibrr.com/kjs/job_board/search"
        self.start_date = None
        self.end_date = None
        self.get_date_range(self.days)

        self.keywords = keywords
        self.log.info("Retrieving job listings from Kalibrr")


    def get_date_range(self, days: int) -> tuple[datetime, datetime]:
        """Calculate the start and end date based on the number of days.

        Args:
            days (int): The number of days to subtract from the current date.

        Returns:
            tuple[datetime, datetime]: A tuple containing the start and end dates.
        """
        
        self.end_date = datetime.now(timezone.utc)  # Current date and time in UTC
        self.start_date = self.end_date - timedelta(days=days)  # Start date calculated by subtracting days
        
        pass 

    def start(self) -> list[JobListing]:
        """
        Main method to handle the complete flow of retrieving job listings.

        This method manages the entire process of fetching and processing
        job listings from Kalibrr's API.

        Returns:
            list[JobListing]: Collection of processed job listings.
                Returns empty list if no listings are found or on error.

        Raises:
            requests.RequestException: If API request fails.
            ValueError: If date range is invalid.
            Exception: For other unexpected errors.

        Example:
            >>> client = KalibrrAPIClient(DateRange.PAST_WEEK)
            >>> listings = client.start()
            >>> print(f"Found {len(listings)} jobs")
        """
        self.log.debug(f"Starting Kalibrr job listings retrieval for date range: {self.days if self.days else 'All'}")
        
        try:
            # Set state to PROCESSING when starting
            
            listings = self.get_listings_by_date_range()
            self.log.debug(f"Successfully retrieved {len(listings)} job listings from Kalibrr")
            
            if not listings:
                self.log.warning("No job listings found for the specified criteria in Kalibrr")
                return listings
            
            # Return the snapshot
            try:
                self.log.info("Finished gathering job listings from Kalibrr")
                return listings
                
            except Exception as e:
                self.log.debug(f"Failed to store job listings snapshot: {str(e)}")
                raise
            
        except requests.RequestException as e:
            self.log.error(f"Failed to fetch job listings from Kalibrr API: {str(e)}")
            raise
        except ValueError as e:
            self.log.error(f"Invalid date range provided: {str(e)}")
            raise
        except Exception as e:
            self.log.error(f"Unexpected error during job listings retrieval: {str(e)}")
            raise

    def get_listings_by_date_range(self) -> list[JobListing]:
        """
        Retrieve and filter job listings based on date range.

        This method handles pagination and date filtering of job listings
        from Kalibrr's API.

        Returns:
            list[JobListing]: Collection of filtered job listings.
                Returns empty list if no listings match criteria.

        Example:
            >>> client = KalibrrAPIClient(DateRange.PAST_WEEK)
            >>> listings = client.get_listings_by_date_range()
        """
        all_listings = []
        offset = 0
        limit = 15
        
        while True:
            self.log.debug(f"Fetching batch of listings - offset: {offset}, limit: {limit}")
            
            try:
                response = self.fetch_listings(limit=limit, offset=offset)
                listings = response.get("jobs", [])
                
                if not listings:
                    self.log.debug("No more listings found")
                    self.log.warning("No listings found on Kalibrr")
                    break
                    
                filtered_listings = []
                for listing in listings:
                    listing_date = datetime.fromisoformat(listing["activation_date"].replace("Z", "+00:00"))
                    
                    if self.start_date and listing_date < self.start_date:
                        self.log.debug(f"Skipping listing {listing['name']}: before start date")
                        continue
                    if self.end_date and listing_date > self.end_date:
                        self.log.debug(f"Skipping listing {listing['name']}: after end date")
                        continue
                        
                    job_listing = self.map_kalibrr_listing_to_job_listing(listing)
                    filtered_listings.append(job_listing)
                    
                if not filtered_listings:
                    self.log.debug("No listings passed the date filter")
                    break
                    
                self.log.debug(f"Added {len(filtered_listings)} listings to results")
                all_listings.extend(filtered_listings)
                offset += limit
                
            except Exception as e:
                self.log.debug(f"Error while retrieving Kalibrr job listings: {str(e)}")
                raise
            
        self.log.info(f"Total listings found on Kalibrr: {len(all_listings)}")

        return all_listings

    def fetch_listings(self, limit=15, offset=0):
        """
        Make API request to fetch job listings with pagination.

        Args:
            limit (int, optional): Number of listings to fetch per request.
                Defaults to 15.
            offset (int, optional): Number of listings to skip.
                Defaults to 0.

        Returns:
            dict: API response containing job listings and metadata.

        Example:
            >>> client = KalibrrAPIClient()
            >>> response = client.fetch_listings(limit=20, offset=40)
        """
        self.log.debug(
            f"Fetching listings with params - limit: {limit}, offset: {offset}, "
            f"start_date: {self.start_date}, end_date: {self.end_date}"
        )

        self.log.debug(f"Using keywords: {self.keywords}")

        params = {
            "limit": limit,
            "offset": offset,
            "country": "Philippines",
            "sort_direction": "desc",
            "sort_field": "activation_date",
            "function": "IT and Software",
        }
        if self.keywords:
            params["text"] = self.keywords


        self.log.debug(f"API request params: {params}")
        
        response = requests.get(self.base_url, params=params)
        self.log.debug(f"API response received with status code: {response.status_code}")
        return response.json()

    def map_kalibrr_listing_to_job_listing(self, listing_data: dict) -> JobListing:
        """
        Convert Kalibrr API response format to JobListing object.

        This method processes raw API data and formats it into a standardized
        JobListing object, including salary formatting and location processing.

        Args:
            listing_data (dict): Raw job listing data from Kalibrr API.

        Returns:
            JobListing: Processed job listing in standard format.

        Example:
            >>> client = KalibrrAPIClient()
            >>> raw_data = client.fetch_listings()['jobs'][0]
            >>> listing = client.map_kalibrr_listing_to_job_listing(raw_data)
        """
        salary = "Not specified"
        if listing_data.get("salary_shown"):
            base = listing_data.get("base_salary")
            maximum = listing_data.get("maximum_salary")
            currency = listing_data.get("salary_currency", "")
            interval = listing_data.get("salary_interval", "")
            
            if base and maximum:
                salary = f"{currency} {base:,} - {maximum:,} per {interval}"
            elif base:
                salary = f"{currency} {base:,} per {interval}"
            elif maximum:
                salary = f"Up to {currency} {maximum:,} per {interval}"

        location_components = listing_data.get("google_location", {}).get("address_components", {})
        location = f"{location_components.get('city', '')}, {location_components.get('region', '')}"
        
        # Clean up the description
        description = listing_data["description"]
        soup = BeautifulSoup(description, 'html.parser')
        
        # Convert <li> items to bullet points
        for li in soup.find_all('li'):
            li.replace_with(f"• {li.get_text().strip()}\n")
        
        # Convert <p> to new lines
        for p in soup.find_all('p'):
            p.replace_with(f"{p.get_text().strip()}\n\n")
        
        # Get clean text and remove extra whitespace
        clean_description = soup.get_text().strip()
        clean_description = '\n'.join(line.strip() for line in clean_description.splitlines() if line.strip())

        # Parse the ISO format date and convert to MM-DD-YY
        listing_date = datetime.fromisoformat(listing_data["activation_date"].split('.')[0]).strftime("%m-%d-%y")

        return JobListing(
            site="Kalibrr",
            listing_date=listing_date,
            job_title=listing_data["name"],
            company=listing_data["company_name"],
            location=location.strip(", "),
            employment_type=listing_data["tenure"],
            position=listing_data.get("function", "IT and Software"),
            salary=salary,
            description=clean_description,
            url=f"https://www.kalibrr.com/c/{listing_data['company']['code']}/jobs/{listing_data['id']}/{listing_data['slug']}"
        )