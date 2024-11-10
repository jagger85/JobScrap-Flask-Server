from logger.logger import get_logger, set_log_level, get_sse_handler
from constants.platforms import Platforms
from constants.date_range import DateRange
from selenium_scrappers.kalibrr.kalibrr_api_request import KalibrrAPIClient
from selenium_scrappers.jobstreet.jobstreet_scrapper_machine import JobstreetScrapperMachine as jobstreet_scrapper
from brightdata.BrightPioneer import BrightPioneer
from config.config import Config
from data_handler import StorageType
import logging
from server.state_manager import StateManager
from server.sse_observer import SSEObserver
from constants.platform_states import PlatformStates
from models.IndeedParams import IndeedParams
from models.LinkedInParams import LinkedInParams

class Operation:
    def __init__(self, date_range: DateRange, platforms: list[Platforms]):
        self.config = Config()
        self.config.platforms = [platform.value for platform in platforms]
        self.config.date_range = date_range
        self.config.storage_type = StorageType.JSON
        self.listings = None
        
        # Initialize data handler
        self.data_handler = self.config.storage

        set_log_level(logging.DEBUG)
        self.log = get_logger("ScraperOperation")
        
        # Initialize state management
        self.state_manager = StateManager()
        self.sse_observer = SSEObserver(get_sse_handler())  # Use singleton handler
        
        # Initialize platforms
        self.platforms = platforms
        for platform in self.platforms:
            self.state_manager.set_platform_state(platform, PlatformStates.WAITING)
            self.log.info(f"Initialized {platform.value}")

    def scrape_all_sites(self):
        self.listings = []
        self.log.info("Starting to collect job listings from all selected platforms...")
        
        platform_handlers = {
            Platforms.JOBSTREET: self.handle_jobstreet,
            Platforms.KALIBRR: self.handle_kalibrr,
            Platforms.LINKEDIN: self.handle_linkedIn,
            Platforms.INDEED: self.handle_indeed,
            Platforms.GOOGLE: self.handle_google
        }

        self.log.debug(f"Configured platforms: {self.config.platforms}")

        for scraper_type in platform_handlers:
            self.log.debug(f"Checking platform: {scraper_type.value}")
            if scraper_type.value in self.config.platforms:
                platform_listings = platform_handlers[scraper_type](scraper_type)
                if platform_listings:
                    self.log.info(f"Got {len(platform_listings)} listings from {scraper_type.value}")
                    self.listings.extend(platform_listings)
            else:
                pass
        
        # Convert JobListing objects using the data handler
        if self.listings:
            self.log.info(f"Successfully collected {len(self.listings)} job listings in total")
            processed_listings = self.data_handler.return_snapshot(self.listings)
            self.config.listings = processed_listings  # Store in config
            self.log.info("Finished processing all job listings")
            return processed_listings
        else:
            self.log.info("No job listings were found. Please try adjusting your search criteria")
            self.config.listings = []
            return []

    def handle_jobstreet(self, platform):
        self.log.info("Starting to collect jobs from Jobstreet")
        self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.PROCESSING)
        mission = jobstreet_scrapper()
        listings = mission.start()
        if listings:
            self.log.info(f"Successfully collected {len(listings)} jobs from Jobstreet")
            self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.FINISHED)
        else:
            self.log.info("No jobs found on Jobstreet for your search criteria")
            self.state_manager.set_platform_state(Platforms.JOBSTREET, PlatformStates.FINISHED)

        return listings

    def handle_kalibrr(self, platform):
        self.log.info("Starting to collect jobs from Kalibrr")
        self.state_manager.set_platform_state(Platforms.KALIBRR, PlatformStates.PROCESSING)
        client = KalibrrAPIClient(date_range=self.config.date_range)
        listings = client.retrieve_job_listings()
        if listings:
            self.log.info(f"Successfully collected {len(listings)} jobs from Kalibrr")
            self.state_manager.set_platform_state(Platforms.KALIBRR, PlatformStates.FINISHED)
        else:
            self.log.info("No jobs found on Kalibrr for your search criteria")
            self.state_manager.set_platform_state(Platforms.KALIBRR, PlatformStates.FINISHED)

        return listings

    def handle_indeed(self, platform):
        self.log.info("Starting to collect jobs from Indeed")
        self.state_manager.set_platform_state(Platforms.INDEED, PlatformStates.PROCESSING)
        params = IndeedParams(date_range=self.config.date_range)
        #TODO implement indeed
        self.state_manager.set_platform_state(Platforms.INDEED, PlatformStates.FINISHED)

    def handle_linkedIn(self, platform):
        self.log.info("Starting to collect jobs from LinkedIn")
        self.state_manager.set_platform_state(Platforms.LINKEDIN, PlatformStates.PROCESSING)
        #TODO implement linkedIn
        params = LinkedInParams(date_range=self.config.date_range)

        self.state_manager.set_platform_state(Platforms.LINKEDIN, PlatformStates.FINISHED)




    def handle_google(self, platform):
        self.log.info("Google Jobs collection is not available at the moment")
        self.state_manager.set_platform_state(Platforms.GOOGLE, PlatformStates.ERROR)

    def get_listings(self):
        return self.listings

if __name__ == "__main__":
    platforms = [Platforms.KALIBRR, Platforms.JOBSTREET]  
    date_range = DateRange.PAST_MONTH
    scraper_operation = Operation(date_range, platforms)
    scraper_operation.scrape_all_sites()
