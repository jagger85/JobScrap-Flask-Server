from logger.logger import get_logger, get_sse_handler
from constants.platforms import Platforms
from constants.date_range import DateRange
from scrappers import kalibrr, jobstreet, brightPioneer
from config.config import Config
from data_handler import StorageType
from server.state_manager import StateManager
from server.sse_observer import SSEObserver
from constants.platform_states import PlatformStates
from models import IndeedParams, LinkedInParams


class Operation:
    """
    Manages scraping operations across multiple job listing platforms.

    This class coordinates the scraping of job listings from various platforms,
    handles state management, and processes the collected data.

    Args:
        date_range (DateRange): The time period for which to collect job listings.
        platforms (list[Platforms]): List of platforms to scrape from.

    Attributes:
        config (Config): Configuration settings for the scraping operation.
        listings (list): Collected job listings from all platforms.
        data_handler: Handler for storing and processing job listings.
        state_manager (StateManager): Manages the state of each platform's operation.
        sse_observer (SSEObserver): Handles Server-Sent Events for real-time updates.
        platforms (list[Platforms]): List of platforms to scrape from.
        platform_handlers (dict): Mapping of platforms to their respective handler classes.
    """

    def __init__(self, user: str, date_range: DateRange, platforms: list[Platforms]):
        self.config = Config()
        self.config.platforms = [platform.value for platform in platforms]
        self.config.date_range = date_range
        self.config.keywords = keywords
        self.config.storage_type = StorageType.JSON
        self.listings = None
        
        # Initialize data handler
        self.data_handler = self.config.storage

        self.log = get_logger("ScraperOperation")
        
        # Initialize state management
        self.state_manager = StateManager()
        self.sse_observer = SSEObserver(get_sse_handler())  # Use singleton handler
        
        # Initialize platforms
        self.platforms = platforms
        for platform in self.platforms:
            self.state_manager.set_platform_state(platform, PlatformStates.WAITING)
            self.log.info(f"Initialized {platform.value}")

        # Define platform handlers mapping only for selected platforms
        self.platform_handlers = {}
        for platform in self.platforms:
            if platform == Platforms.JOBSTREET:
                self.platform_handlers[platform] = (jobstreet_scrapper, {'keywords': self.config.keywords})
            elif platform == Platforms.KALIBRR:
                self.platform_handlers[platform] = (KalibrrAPIClient, {'date_range': self.config.date_range, 'keywords': self.config.keywords})
            elif platform == Platforms.LINKEDIN:
                self.platform_handlers[platform] = (BrightPioneer, {'params': LinkedInParams(date_range=self.config.date_range, keywords=self.config.keywords)})
            elif platform == Platforms.INDEED:
                self.platform_handlers[platform] = (BrightPioneer, {'params': IndeedParams(date_range=self.config.date_range, keywords=self.config.keywords)})


    def _handle_platform(self, platform: Platforms) -> list:
        """
        Process job listings collection for a specific platform.

        This method initializes the appropriate scraper for the given platform,
        manages its state, and handles any errors during the scraping process.

        Args:
            platform (Platforms): The platform to scrape from.

        Returns:
            list: Collection of job listings from the platform.
                Returns empty list if scraping fails or no jobs are found.

        Example:
            >>> operation = Operation(DateRange.PAST_MONTH, [Platforms.JOBSTREET])
            >>> listings = operation._handle_platform(Platforms.JOBSTREET)
        """
        self.log.info(f"Starting to collect jobs from {platform.value}")
        
        handler_info = self.platform_handlers.get(platform)
        if not handler_info:
            self.log.warning(f"{platform.value} collection is not available at the moment")
            self.state_manager.set_platform_state(platform, PlatformStates.ERROR)
            return []

        handler_class, kwargs = handler_info
        try:
            scraper = handler_class(**kwargs) if kwargs else handler_class()
            listings = scraper.start()
            
            if listings:
                self.log.info(f"Successfully collected {len(listings)} jobs from {platform.value}")
            else:
                self.log.info(f"No jobs found on {platform.value} for your search criteria")
                
            return listings
            
        except Exception as e:
            self.log.error(f"Error processing {platform.value}: {str(e)}")
            self.state_manager.set_platform_state(platform, PlatformStates.ERROR)
            return []

    def scrape_all_sites(self):
        """
        Collect job listings from all configured platforms.

        This method coordinates the scraping process across all selected platforms,
        processes the collected listings through the data handler, and stores
        the results in the configuration.

        Returns:
            list: Processed job listings from all platforms.
                Returns empty list if no listings are found.

        Example:
            >>> operation = Operation(DateRange.PAST_MONTH, [Platforms.KALIBRR])
            >>> listings = operation.scrape_all_sites()
        """
        self.listings = []
        self.log.info("Starting to collect job listings from all selected platforms...")
        
        for platform in self.platforms:
            if platform.value in self.config.platforms:
                platform_listings = self._handle_platform(platform)
                if platform_listings:
                    self.listings.extend(platform_listings)

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
            self.config.reset_to_defaults()
            self.state_manager.initialize_platform_states()
            return

    def get_listings(self):
        """
        Retrieve the collected job listings.

        Returns:
            list: The current collection of job listings.
                Returns None if no scraping has been performed yet.
        """
        return self.listings

if __name__ == "__main__":
    platforms = [Platforms.KALIBRR, Platforms.JOBSTREET]  
    date_range = DateRange.PAST_MONTH
    scraper_operation = Operation(date_range, platforms)
    scraper_operation.scrape_all_sites()
