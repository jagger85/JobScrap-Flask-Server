from logger import get_logger, set_log_level
from selenium_mission import Mission
from kalibrr.kalibrr_scrapper_machine import KalibrrScrapperMachine as voyager
from jobstreet.jobstreet_scrapper_machine import JobstreetScrapperMachine as voyager2
import logging
from enum import Enum

set_log_level(logging.INFO)

log = get_logger('Control station')

# Define the enum class
class ScraperType(Enum):
    Jobstreet = 1
    Kalibrr = 2

# Define a mapping from ScraperType to URLs
scraper_urls = {
   # ScraperType.Jobstreet: [
  #      'https://www.jobstreet.com.ph/react-jobs?sortmode=ListedDate'
 #   ],
    ScraperType.Kalibrr: [
        "https://www.kalibrr.com/home/te/tech-position/co/Philippines/i/it-and-software?sort=Freshness",
        #"https://www.kalibrr.com/home/te/tech-position/co/Philippines/i/accounting-and-finance/i/administration-and-coordination/i/architecture-and-engineering/i/arts-and-sports/i/customer-service/i/education-and-training/i/general-services/i/health-and-medical/i/hospitality-and-tourism/i/human-resources/i/it-and-software/i/legal/i/management-and-consultancy/i/manufacturing-and-production/i/media-and-creatives/i/public-service-and-ngos/i/safety-and-security/i/sales-and-marketing/i/sciences/i/supply-chain/i/writing-and-content?sort=Freshness"
    ]
}

def scrape_all_sites():
    for scraper_type, urls in scraper_urls.items():
        for url in urls:
            log.info(f'📍 Expedition: {url} for {scraper_type.name}')
            if scraper_type == ScraperType.Jobstreet:
                Mission(get_logger('Jobstreet'), url, voyager2).start()
            elif scraper_type == ScraperType.Kalibrr:
                Mission(get_logger('Kalibrr'), url, voyager).start()

if __name__ == "__main__":
    log.info('🏢 Initiating digital expeditions - May the bandwidth be ever in our favor! 🌟')
    scrape_all_sites()
