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
            # Initialize Chrome driver with project-relative path
            log.debug("🔧 Initializing Chrome driver")
            chromedriver_path = "./chromedriver"
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
        try:
            self.get_job_listings()
            self.process_listings() 
        except Exception as e:
            log.error(f"Error in loading_listings: {str(e)}")
            self.error_occurred(str(e))

    def on_enter_processing_listings(self):
        try:
            self.send_result(self.process_job_listings())

        except Exception as e:
            log.error(f"Error in processing_listings: {str(e)}")
            self.error_occurred(str(e))

    def on_enter_sending_listings(self, listings: List[JobListing]):
        try:
            log.debug("🛰️  Sending result")
            self.final_listings = listings  

        except Exception as e:
            log.error(f"Error in sending_listings: {str(e)}")
            self.error_occurred(str(e))
            self.final_listings = []

    def on_enter_error(self, msg):
        log.error(f"❌ error: {msg}")
        pass
    
    def start(self):
        try:
            self.final_listings = []  
            self.launch()
            return self.final_listings 

        finally:
            self.cleanup()

    # # Every scrapper who inherits from this base must implement this methods

    @abstractmethod
    def get_job_listings(self):
        pass

    @abstractmethod
    def process_job_listings(self) ->List[JobListing]:
        pass

    @abstractmethod
    def process_error(self):
        pass

    def cleanup(self):
        if self.driver:
            log.debug("🧹 Cleaning up Chrome driver")
            self.driver.quit()
            self.driver = None
            self.config.chrome_driver = None
            log.debug("✨ Chrome driver cleaned up successfully")
        else:
            log.debug("🤷 No Chrome driver to clean up")

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
