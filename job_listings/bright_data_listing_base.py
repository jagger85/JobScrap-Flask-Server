from abc import ABC, abstractmethod
from datetime import datetime


# Define an abstract class with both abstract and concrete methods
class BrightDataListingBase(ABC):
    @abstractmethod
    def get_job_listings(self):
        """Method that sends the request to the server an returns a json file ."""
        pass

    @abstractmethod
    def collect_data(self, data):
        """Method that recieves a json file and"""

    def format_date(self, date_string):
        if date_string == "unspecified":
            return date_string
        try:
            # Parse the ISO 8601 format date string
            date_obj = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            return date_obj.strftime("%B %d, %Y")  # Format as "Month Day, Year"
        except ValueError:
            return date_string  # Return original string if parsing fails

    def get_value(self, data, key):
        value = data.get(key, None)
        return "unspecified" if value is None else value
