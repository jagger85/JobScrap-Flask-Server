from logger.logger import get_logger, set_log_level
from selenium_scrappers import SeleniumMission
from constants.platforms import Platforms
from constants.date_range import DateRange
from selenium_scrappers.kalibrr.kalibrr_api_request import KalibrrAPIClient
from config import Config
from data_handler import StorageType
import logging
from server.state_manager import StateManager
from server.sse_observer import SSEObserver
from constants.platform_states import PlatformStates

class Operation:
    def __init__(self, date_range: DateRange, platforms: list[Platforms]):
        self.config = Config()
        self.config.platforms = [platform.value for platform in platforms]
        self.config.date_range = date_range
        self.config.storage_type = StorageType.CSV

        set_log_level(logging.DEBUG)
        self.log = get_logger("ScraperOperation")
        
        # Initialize state management
        self.state_manager = StateManager()
        self.sse_observer = SSEObserver(self.log.handlers[1])  # Get SSE handler from logger
        self.state_manager.add_observer(self.sse_observer)
        
        # Initialize platforms
        self.platforms = platforms
        for platform in self.platforms:
            self.state_manager.set_platform_state(platform, PlatformStates.WAITING)
            self.log.info(f"Initialized {platform.value}")

    def scrape_all_sites(self):
        # Platform-specific scraping handlers
        platform_handlers = {
            Platforms.JOBSTREET: self.handle_jobstreet,
            Platforms.KALIBRR: self.handle_kalibrr,
            # More platforms here
        }

        self.log.debug(f"Configured platforms: {self.config.platforms}")

        for scraper_type in platform_handlers:
            self.log.debug(f"Checking platform: {scraper_type.value}")
            if scraper_type.value in self.config.platforms:
                platform_handlers[scraper_type](scraper_type)
                
            else:
                self.log.debug(
                    f"Skipping platform: {scraper_type.name} as it is not enabled in config"
                )

    def handle_jobstreet(self, platform):
        mission = SeleniumMission(get_logger(platform.name), platform)
        mission.start()

    def handle_kalibrr(self, platform):
        client = KalibrrAPIClient(self.config.storage, self.config.date_range)
        client.retrieve_job_listings()
        

    def handle_indeed(self, platform):
        self.log.warning("Operation Indeed not implemented yet")

    def handle_linkedIn(self, platform):
        self.log.warning("Operation linkedIn not implemented yet")

    def handle_google(self, platform):
        self.log.warning("Operation google not implemented yet")


if __name__ == "__main__":
    platforms = [Platforms.KALIBRR, Platforms.JOBSTREET]  
    date_range = DateRange.PAST_MONTH
    scraper_operation = Operation(date_range, platforms)
    scraper_operation.scrape_all_sites()
