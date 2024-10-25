from bs4 import BeautifulSoup
from bs4 import Comment  # Add this import for comment removal
import csv
from scrape import scrape_website

base_URL = "https://www.kalibrr.com/home/co/Philippines/"


def create_kalibrr_URL(keywords):
    """
    Create a Kalibrr search URL based on given keywords.

    :param keywords: List of search terms
    :return: Formatted URL string for Kalibrr job search
    """
    return base_URL + f"te/{'-'.join(keywords)}"


def scrape_kalibrr(keywords):
    """
    Main function to scrape Kalibrr job listings.

    :param keywords: List of search terms
    """
    url = create_kalibrr_URL(keywords)
    DOM_content = scrape_website(url)
    clean_dom(DOM_content)


def clean_dom(DOM_content):
    """
    Clean and simplify the DOM content from Kalibrr.

    This function removes unnecessary tags, comments, and attributes,
    and writes the cleaned content to a file.

    :param DOM_content: Raw HTML content from Kalibrr
    """
    # Parse the HTML content
    soup = BeautifulSoup(DOM_content, "html.parser")

    # Tags to remove
    tags_to_remove = [
        "script",
        "style",
        "iframe",
        "noscript",
        "head",
        "meta",
        "link",
        "header",
        "footer",
        "nav",
        "svg",
        "path",
    ]

    # Remove unwanted tags
    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove all comments
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove class attribute from div, a, h2, span, and img tags
    for tag in soup.find_all(["div", "a", "h2", "span", "img"]):
        del tag["class"]

    # Remove empty div tags
    def remove_empty_divs(soup):
        for div in soup.find_all("div"):
            if len(div.get_text(strip=True)) == 0 and len(div.find_all(True)) == 0:
                div.decompose()
            else:
                remove_empty_divs(div)

    remove_empty_divs(soup)

    # Get the cleaned HTML content
    cleaned_content = soup.prettify()

    # Write the cleaned content to a file
    with open("cleaned_kalibrr_dom.html", "w", encoding="utf-8") as file:
        file.write(cleaned_content)

    print("Cleaned DOM content has been written to 'cleaned_kalibrr_dom.html'")

    extract_jobs(cleaned_content)


def extract_jobs(content):
    """
    Extract job listings from the cleaned DOM content.

    This function parses the cleaned HTML, extracts relevant job information,
    and prints each job's details.

    :param content: Cleaned HTML content
    """
    soup = BeautifulSoup(content, "html.parser")
    job_listings = soup.find_all("div", itemtype="http://schema.org/ItemList")

    jobs = []
    for listing in job_listings:
        job_divs = listing.find_all("div", recursive=False)
        for job_div in job_divs:
            # Check if this div contains a job title
            if job_div.find("h2"):
                job_content = []
                job_link = ""
                for element in job_div.children:
                    if element.name == "a" and element.get("href"):
                        job_content.append(element.get_text(strip=True))
                        job_link = element["href"]
                    elif element.name and element.stripped_strings:
                        for string in element.stripped_strings:
                            job_content.append(string)
                        for link in element.find_all("a", href=True):
                            # Only add "View Post" if it has a non-empty href
                            if (
                                link.get_text(strip=True) == "View Post"
                                and link["href"]
                            ):
                                job_content.append("View Post")
                if job_link:
                    job_content.append(f"Job link: {job_link}")
                jobs.append("\n".join(job_content))

    if jobs:
        # Print extracted jobs
        print(f"Number of jobs found: {len(jobs)}")
        for i, job in enumerate(jobs, 1):
            print(f"Job {i}:")
            print(job)
            print("-" * 50)  # Separator between jobs
    else:
        print(f"No jobs found.")
