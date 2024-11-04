from config import Config
from .kalibrr.kalibrr_scrapper_machine import KalibrrScrapperMachine
from .jobstreet.jobstreet_scrapper_machine import JobstreetScrapperMachine
from models.platforms import Platforms
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

"""
    Core functionality for web scraping orchestration.

    This class handles the initialization and management of web scraping operations
    by dynamically creating the appropriate scraper machine based on the provided type.

    Args:
        logger: Logger instance for operation tracking
        scraper_type (Platforms): Enum indicating which scraper implementation to use
                                   (JOBSTREET or KALIBRR)

    Returns:
        None: Class initializes scraping environment and manages lifecycle

    Raises:
        ValueError: When an unsupported scraper type is provided
        Exception: When scraper initialization fails

    Example:
        >>> logger = get_logger('Kalibrr')
        >>> mission = SeleniumMission(logger, Platforms.KALIBRR)
        >>> mission.start()
"""

class SeleniumMission():
    def __init__(self, logger, scraper_type: Platforms):
        self.logger = logger
        self.config = Config()
        
        try:
            # Initialize Chrome driver with project-relative path
            self.logger.debug("🔧 Initializing Chrome driver")
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chromedriver_path = os.path.join(current_dir, "chromedriver")
            service = Service(chromedriver_path)
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.config.chrome_driver = self.driver  # Set reference in config
            
            # Initialize scraper based on type
            if scraper_type == Platforms.JOBSTREET:
                self.scrapping_probe = JobstreetScrapperMachine(self.logger)
            elif scraper_type == Platforms.KALIBRR:
                self.scrapping_probe = KalibrrScrapperMachine(self.logger)
            else:
                raise ValueError(f"Unsupported scraper type: {scraper_type}")
                
            self.logger.info(f'🎯 Initialized {scraper_type.value} scraper')
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize scraper: {str(e)}")
            self.cleanup()
            raise

    def start(self):
        try:
            self.logger.info('🚀  Launching')
            self.scrapping_probe.launch()

        finally:
            self.cleanup()

    def cleanup(self):
        if self.driver:
            self.logger.debug("🧹 Cleaning up Chrome driver")
            self.driver.quit()
            self.driver = None
            self.config.chrome_driver = None
            self.logger.debug("✨ Chrome driver cleaned up successfully")
        else:
            self.logger.debug("🤷 No Chrome driver to clean up")

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
