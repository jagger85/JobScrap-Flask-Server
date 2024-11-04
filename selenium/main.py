from logger.logger import get_logger, set_log_level
from selenium_mission import SeleniumMission
from models.platforms import Platforms
from models.date_range import DateRange
from config import Config
from data_handler.storage_type import StorageType
import logging

# Initialize config
config = Config()
config.platforms = [Platforms.JOBSTREET.value, Platforms.KALIBRR.value]  # Use enum values

config.date_range = DateRange.PAST_24_HOURS
config.storage_type = StorageType.CSV


set_log_level(logging.DEBUG)

log = get_logger("Control station")


def scrape_all_sites():
    # Configure scrapers to run
    scrapers = [Platforms.JOBSTREET,Platforms.KALIBRR]  # Ensure both platforms are included

    log.debug(f"Configured platforms: {config.platforms}")

    for scraper_type in scrapers:
        log.debug(f"Checking platform: {scraper_type.value}")
        if scraper_type.value in config.platforms:  # Only run if platform is enabled in config
            log.info(f"📍 Starting expedition for {scraper_type.name}")
            mission = SeleniumMission(get_logger(scraper_type.name), scraper_type)
            mission.start()
        else:
            log.info(f"Skipping platform: {scraper_type.name} as it is not enabled in config")


if __name__ == "__main__":
    log.info(
        "🏢 Initiating digital expeditions - May the bandwidth be ever in our favor! 🌟"
    )

    try:
        scrape_all_sites()
    finally:
        if config.chrome_driver:
            config.chrome_driver.quit()
