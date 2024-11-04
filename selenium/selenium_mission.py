from config import Config
from kalibrr.kalibrr_scrapper_machine import KalibrrScrapperMachine
from jobstreet.jobstreet_scrapper_machine import JobstreetScrapperMachine
from models.platforms import Platforms

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
            raise

    def start(self):
        try:
            self.logger.info('🚀  Launching')
            self.scrapping_probe.launch()

        finally:
            self.cleanup()

    def cleanup(self):
        Config().chrome_driver.quit()

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
