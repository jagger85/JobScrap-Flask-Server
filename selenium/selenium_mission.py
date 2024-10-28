from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
"""
    Core functionality for async web scraping initialization.

    This class handles the setup and management of async web scraping operations
    using Selenium WebDriver.

    Args:
        logger: Logger instance for operation tracking
        base_url (str): Target website's base URL
        scrapper: State machine instance for scraping operations

    Returns:
        None: Class initializes scraping environment and manages lifecycle

    Raises:
        Exception: When page loading fails or driver setup encounters issues

    Example:
        >>> logger = Logger()
        >>> mission = Mission(logger, "https://example.com", ScrapperMachine)
        >>> voyager.start()
"""

class Mission():
    def __init__(self,logger, url, scrapper):
        global log
        log = logger
        
        self.scrapper = scrapper
        self.url = url
        self.setup_driver()

    def setup_driver(self):
        service = Service("selenium/chromedriver")
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=service, options=options)

        try:
            self.driver.get(self.url)
            log.info(f'🎯  Target <-{self.url}-> loaded successfully')
        except Exception as e:
            log.error(f"❌  Failed to load page / {self.url} / {str(e)}")
            raise
        
        self.scrapping_probe = self.scrapper(log,self.driver)

    def start(self):
        try:
            log.info('🚀  Launching')
            self.scrapping_probe.launch()

        finally:
            self.cleanup()

    def cleanup(self):
        self.driver.quit

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
