from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class IndeedParams:
    """
    A class to represent Indeed job search parameters.
    """

    location: str
    keywords: str
    country: str = field(default="PH", init=False)
    domain: str = field(default="ph.indeed.com", init=False)

    def __post_init__(self):
        """
        Validate the types and values of fields after initialization.
        """

        if not isinstance(self.location, str) or not self.location.strip():
            raise ValueError("Location must be a non-empty string")

    def to_dict(self) -> Dict:
        """
        Convert the IndeedParams object to a dictionary.

        Returns:
            Dict: A dictionary representation of the IndeedParams object.
        """
        result = {
            "country": self.country,
            "domain": self.domain,
            "location": self.location,
            "keyword_search": self.keywords,
        }

        return result

    def __dict__(self):
        return self.to_dict()
