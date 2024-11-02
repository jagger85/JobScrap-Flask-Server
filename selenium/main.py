from logger.logger import get_logger, set_log_level
from selenium_mission import SeleniumMission, ScraperType
from models.date_range import DateRange
from config import Config
from data_handler.storage_type import StorageType
import logging

# Initialize config
config = Config()
config.platforms = ["Jobstreet"]

# Initialize the Chrome driver
config.init_chrome_driver(headless=True)
config.date_range = DateRange.PAST_15_DAYS
config.storage_type = StorageType.CSV


set_log_level(logging.DEBUG)

log = get_logger("Control station")


def scrape_all_sites():
    # Configure scrapers to run
    scrapers = [(ScraperType.KALIBRR, "Kalibrr"), (ScraperType.JOBSTREET, "Jobstreet")]

    for scraper_type, name in scrapers:
        if name in config.platforms:  # Only run if platform is enabled in config
            log.info(f"📍 Starting expedition for {name}")
            mission = SeleniumMission(get_logger(name), scraper_type)
            mission.start()


if __name__ == "__main__":
    log.info(
        "🏢 Initiating digital expeditions - May the bandwidth be ever in our favor! 🌟"
    )

    try:
        scrape_all_sites()
    finally:
        if config.chrome_driver:
            config.chrome_driver.quit()
