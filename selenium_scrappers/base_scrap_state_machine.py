from transitions import Machine
from abc import ABC, abstractmethod
from models import JobListing
from typing import List
from config.config import Config
from server.state_manager import StateManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from functools import lru_cache
from webdriver_manager.chrome import ChromeDriverManager

states = [
    "idle",
    "loading_listings",
    "processing_listings",
    "sending_listings",
    "error",
]

# TRANSITIONS
# A transition happens when a trigger is called
# Each transition has a source (current state) and a dest (destination state)
# Error_occurred: Moves the machine to error from any state ('*' represents any state)

transitions = [
    {"trigger": "launch", "source": "*", "dest": "loading_listings"},
    {"trigger": "load_listings", "source": "idle", "dest": "loading_listings"},
    {
        "trigger": "process_listings",
        "source": "loading_listings",
        "dest": "processing_listings",
    },
    {
        "trigger": "send_result",
        "source": "processing_listings",
        "dest": "sending_listings",
    },
    {"trigger": "error_occurred", "source": "*", "dest": "error"},
]

@lru_cache(maxsize=1)
def get_driver_path():
    return ChromeDriverManager().install()

class BaseScrapStateMachine(ABC):
    """
    BaseScrapeState provides the core state machine functionality for scraping operations.
    This abstract base class defines the common states and transitions that all scrapers share.

    Args:
        scraper: Reference to the voyager instance implementing required methods

    Attributes:
        states (list): Available states in the scraping workflow
        transitions (list): Defined state transitions
        current_page (int): Current page being scraped
        total_jobs (int): Total number of jobs scraped
        failed_attempts (int): Count of failed scraping attempts

    Triggers:
        launch: Moves to loading_listings state from any state
        load_listings: Moves from idle to loading_listings state
        process_listings: Moves from loading_listings to processing_listings state
        send_result: Moves from processing_listings to sending_listings state
        error_occurred: Moves to error state from any state
    """
    
    def __init__(self, logger):
        global log
        log = logger
        self.config = Config()
        self.state_manager = StateManager()
        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="idle"
        )
        log.debug('Starting Mission 🫡')
        self.date_range = Config().date_range
        try:
            log.debug("🔧 Initializing Chrome driver")
            options = Options()
            
            # Headless mode
            options.add_argument("--headless=new")
            
            # Security and stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Performance optimization
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-notifications")
            
            # Set viewport size (needed even in headless mode)
            options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(
                service=Service(get_driver_path()),
                options=options
            )
            self.config.chrome_driver = self.driver
                
        except Exception as e:
            log.error(f"❌ Failed to initialize scraper: {str(e)}")
            self.cleanup()
            raise
        
    # Every trigger launch one of this methods, eg. self.launch() triggers on_enter_loading() and so on

    def on_enter_loading_listings(self):
        """
        Handle state transition to loading_listings.

        This method is automatically called when entering the loading_listings state.
        It initiates the job listing collection process.

        Raises:
            Exception: If listing collection fails, transitions to error state.

        Example:
            >>> machine.launch()  # Triggers on_enter_loading_listings
        """
        try:
            self.get_job_listings()
            self.process_listings() 
        except Exception as e:
            log.error(f"Error in loading_listings: {str(e)}")
            self.error_occurred(str(e))

    def on_enter_processing_listings(self):
        """
        Handle state transition to processing_listings.

        This method is automatically called when entering the processing_listings state.
        It processes raw listing data into structured format.

        Raises:
            Exception: If processing fails, transitions to error state.
        """
        try:
            self.send_result(self.process_job_listings())

        except Exception as e:
            log.error(f"Error in processing_listings: {str(e)}")
            self.error_occurred(str(e))

    def on_enter_sending_listings(self, listings: List[JobListing]):
        """
        Handle state transition to sending_listings.

        Args:
            listings (List[JobListing]): Processed job listings to be sent.

        Raises:
            Exception: If sending fails, transitions to error state and sets empty result.
        """
        try:
            log.debug("🛰️  Sending result")
            self.final_listings = listings  

        except Exception as e:
            log.error(f"Error in sending_listings: {str(e)}")
            self.error_occurred(str(e))
            self.final_listings = []

    def on_enter_error(self, msg):
        """
        Handle state transition to error state.

        Args:
            msg (str): Error message describing the failure.
        """
        log.error(f"❌ error: {msg}")
        pass
    
    def start(self):
        """
        Initialize and execute the scraping process.

        This method manages the complete scraping lifecycle, including
        resource cleanup.

        Returns:
            list: Collection of processed job listings.
                Returns empty list if scraping fails.

        Example:
            >>> scrapper = MyScrapperMachine(logger)
            >>> listings = scrapper.start()
        """
        try:
            self.final_listings = []  
            self.launch()
            return self.final_listings 

        finally:
            self.cleanup()

    # # Every scrapper who inherits from this base must implement this methods

    @abstractmethod
    def get_job_listings(self):
        """
        Abstract method for retrieving job listings.

        This method must be implemented by concrete scraper classes to
        define platform-specific listing collection logic.

        Returns:
            list: Collection of raw job listings.

        Raises:
            NotImplementedError: If not implemented by concrete class.
        """
        pass

    @abstractmethod
    def process_job_listings(self) ->List[JobListing]:
        """
        Abstract method for processing job listings.

        This method must be implemented by concrete scraper classes to
        define platform-specific listing processing logic.

        Returns:
            List[JobListing]: Collection of processed job listings.

        Raises:
            NotImplementedError: If not implemented by concrete class.
        """
        pass

    @abstractmethod
    def process_error(self):
        """
        Abstract method for error handling.

        This method must be implemented by concrete scraper classes to
        define platform-specific error handling logic.

        Raises:
            NotImplementedError: If not implemented by concrete class.
        """
        pass

    def cleanup(self):
        """
        Clean up resources used during scraping.

        This method ensures proper cleanup of the Chrome driver and
        associated resources.

        Example:
            >>> scrapper = MyScrapperMachine(logger)
            >>> try:
            >>>     listings = scrapper.start()
            >>> finally:
            >>>     scrapper.cleanup()
        """
        if self.driver:
            log.debug("🧹 Cleaning up Chrome driver")
            self.driver.quit()
            self.driver = None
            self.config.chrome_driver = None
            log.debug("✨ Chrome driver cleaned up successfully")
        else:
            log.debug("🤷 No Chrome driver to clean up")

    def __aenter__(self):
        """
        Async context manager entry point.

        Returns:
            BaseScrapStateMachine: Instance of the scraper.
        """
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.

        Ensures cleanup is performed when exiting the context.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Exception traceback if an error occurred.
        """
        self.cleanup()
