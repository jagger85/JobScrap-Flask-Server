from transitions import Machine
from abc import ABC, abstractmethod
from models.JobListing import JobListing
from typing import List
from config.config import Config
from server.state_manager import StateManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

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

class BaseScrapStateMachine(ABC):
    """
    Abstract base class for scraping state machines.

    This class provides the core state machine functionality for scraping operations,
    defining common states, transitions, and error handling mechanisms.

    Args:
        logger (Logger): Logger instance for tracking operations.

    Attributes:
        config (Config): Application configuration settings.
        state_manager (StateManager): Manages the scraping operation state.
        machine (Machine): State machine controlling the scraping workflow.
        driver (WebDriver): Selenium WebDriver instance for browser automation.
        date_range (DateRange): Time period filter for job listings.
        final_listings (list): Collection of processed job listings.

    States:
        - idle: Initial state
        - loading_listings: Fetching job listings
        - processing_listings: Processing raw listings data
        - sending_listings: Preparing results for transmission
        - error: Error handling state

    Example:
        >>> class MyScrapperMachine(BaseScrapStateMachine):
        >>>     def get_job_listings(self):
        >>>         # Implementation
        >>>         pass
    """
    
    def __init__(self, logger):
        """
        Initialize the state machine with required components.

        Args:
            logger (Logger): Logger instance for operation tracking.

        Raises:
            Exception: If Chrome driver initialization fails.
        """
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
            # Initialize Chrome driver with project-relative path
            log.debug("🔧 Initializing Chrome driver")
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            chromedriver_path = os.path.join(current_dir, "chromedriver")
            service = Service(chromedriver_path)
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.config.chrome_driver = self.driver  # Set reference in config
                
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
