from datetime import datetime, timezone, timedelta
import requests
from models.date_range import DateRange
from models.JobListing import JobListing
from logger.logger import get_logger
from data_handler.base_data_handler import BaseDataHandler

class KalibrrAPIClient:
    def __init__(self, data_handler: BaseDataHandler, date_range: DateRange = None):
        self.log = get_logger("KALIBRR")
        self.base_url = "https://www.kalibrr.com/kjs/job_board/search"
        self.data_handler = data_handler
        self.date_range = date_range
        
        if date_range:
            self.start_date, self.end_date = self.get_date_range(date_range)
            self.log.info(f"Initialized KalibrrAPIClient with date range: {date_range.value}")
            self.log.debug(f"Date range set to: {self.start_date} - {self.end_date}")
        else:
            self.start_date, self.end_date = None, None
            self.log.info("Initialized KalibrrAPIClient without date range")

    def get_date_range(self, range_type: DateRange) -> tuple[datetime, datetime]:
        end_date = datetime.now(timezone.utc)
        
        if range_type == DateRange.PAST_24_HOURS:
            start_date = end_date - timedelta(days=1)
        elif range_type == DateRange.PAST_WEEK:
            start_date = end_date - timedelta(weeks=1)
        elif range_type == DateRange.PAST_15_DAYS:
            start_date = end_date - timedelta(days=15)
        elif range_type == DateRange.PAST_MONTH:
            start_date = end_date - timedelta(days=30)
        else:
            raise ValueError(f"Unsupported date range: {range_type}")
            
        return start_date, end_date

    def retrieve_job_listings(self) -> list[JobListing]:
        """
        Main method to handle the complete flow of retrieving job listings from Kalibrr
        and storing them using the data handler.
        
        Returns:
            list[JobListing]: List of job listings matching the criteria.
        """
        self.log.info(f"Starting Kalibrr job listings retrieval for date range: {self.date_range.value if self.date_range else 'All'}")
        
        try:
            listings = self.get_listings_by_date_range()
            self.log.info(f"Successfully retrieved {len(listings)} job listings from Kalibrr")
            
            if not listings:
                self.log.warning("No job listings found for the specified criteria")
                return listings
            
            # Store the snapshot
            try:
                self.log.debug("Storing job listings snapshot")
                self.data_handler.store_snapshot(listings)
                self.log.info("Successfully stored job listings snapshot")
            except Exception as e:
                self.log.error(f"Failed to store job listings snapshot: {str(e)}")
                raise
            
            return listings
            
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
        all_listings = []
        offset = 0
        limit = 15
        
        while True:
            self.log.debug(f"Fetching batch of listings - offset: {offset}, limit: {limit}")
            response = self.fetch_listings(limit=limit, offset=offset)
            listings = response.get("jobs", [])
            
            if not listings:
                self.log.debug("No more listings found")
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
            
        self.log.debug(f"Total listings retrieved: {len(all_listings)}")
        return all_listings

    def fetch_listings(self, limit=15, offset=0):
        self.log.debug(
            f"Fetching listings with params - limit: {limit}, offset: {offset}, "
            f"start_date: {self.start_date}, end_date: {self.end_date}"
        )
        
        params = {
            "limit": limit,
            "offset": offset,
            "country": "Philippines",
            "function": "IT and Software",
            "sort_direction": "desc",
            "sort_field": "activation_date"
        }
        
        if self.start_date:
            params["start_date"] = self.start_date.isoformat()
        if self.end_date:
            params["end_date"] = self.end_date.isoformat()
        
        response = requests.get(self.base_url, params=params)
        self.log.debug(f"API response received with status code: {response.status_code}")
        return response.json()

    def map_kalibrr_listing_to_job_listing(self, listing_data: dict) -> JobListing:
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
        
        return JobListing(
            site="Kalibrr",
            listing_date=listing_data["activation_date"],
            job_title=listing_data["name"],
            company=listing_data["company_name"],
            location=location.strip(", "),
            employment_type=listing_data["tenure"],
            position=listing_data.get("function", "IT and Software"),
            salary=salary,
            description=listing_data["description"],
            url=f"https://www.kalibrr.com/c/{listing_data['company']['code']}/jobs/{listing_data['slug']}"
        )

# Example usage:
if __name__ == "__main__":
    from data_handler.json_data_handler import JsonDataHandler  # Example handler
    
    data_handler = JsonDataHandler()
    client = KalibrrAPIClient(
        data_handler=data_handler,
        date_range=DateRange.PAST_WEEK
    )
    
    try:
        listings = client.retrieve_job_listings()
        for listing in listings:
            print(f"{listing.job_title} - {listing.listing_date}")
    except Exception as e:
        print(f"Error: {str(e)}")