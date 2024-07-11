from lxml import html
import random
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3 import Retry

# List of user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
]


# get source code of main page
def fetch_page(url):
    # Set the headers
    headers = {'User-Agent': random.choice(USER_AGENTS), "Accept-Encoding": "*", "Connection": "keep-alive"}
    # Create a request session
    session = requests.Session()
    # Setup retry configuration
    retry = Retry(
        total=5,
        read=5,
        connect=5,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    # Scrape the data by reading content from the URL
    response = session.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    if response.status_code == 429:
        # Wait for a longer period and retry
        print("Rate limit hit. Waiting for 60 seconds...")
        time.sleep(60)
        return fetch_page(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    return response.content


# exacting property details of main page
def fetch_rightmove_listings(url):
    properties = []
    print(f"Page url: {url}")
    time.sleep(5)  # sleep time between requests
    print("Came out of sleep to compute the property listing")
    page_content = fetch_page(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    print("Got the html page content from the URL")
    # Find all property listings
    listings = soup.find_all('div', class_='propertyCard')
    print("Got the listings from the property card")
    # Extract and print details for each listing
    try:
        for listing in listings:
            title = listing.find('h2', class_='propertyCard-title').text.strip()
            description = listing.find_next('div', class_='propertyCard-description').text.strip()
            address = listing.find('address', class_='propertyCard-address').text.strip()
            price = listing.find('div', class_='propertyCard-priceValue').text.strip()
            link = listing.find('a', class_='propertyCard-link')['href']
            property_link = f"https://www.rightmove.co.uk{link}"
            added_on = listing.find('span', class_='propertyCard-branchSummary-addedOrReduced').text.strip()
            agent_contact_number = listing.find('a', class_='propertyCard-contactsPhoneNumber').text.strip()
            agency_details = listing.find('span', class_='propertyCard-branchSummary-branchName').text.strip()

            property_details = fetch_property_details(property_link)
            property_details.update(
                {
                    'title': title,
                    'description': description,
                    'address': address, 'price': price,
                    'link': property_link,
                    'addedOn': added_on,
                    'agentContactNumber': agent_contact_number,
                    'agencyDetails': agency_details
                }
            )
            properties.append(property_details)
    except AttributeError as e:
        # Handle cases where some details might not be present in the listing
        print(f"Error extracting details for a listing: {e}")
    print("Successfully extracted all the listing details from the url")
    return properties


# extracting property details based on each property card(url)
def fetch_property_details(url):
    # fetches all content for every property card
    page_content = fetch_page(url)
    tree = html.fromstring(page_content)

    details = {
        'property_type': None,
        'number_of_bedrooms': None,
        'number_of_bathrooms': None,
        'property_size': None,
        'tenure': None,
    }

    # Extract details based on common patterns found on the property page
    try:
        details['property_type'] = tree.xpath(
            '//dl[@id="info-reel"]//span[text()="PROPERTY TYPE"]/../../dd//span/p/text()')
    except:
        details['property_type'] = "N/A"

    try:
        details['number_of_bedrooms'] = tree.xpath(
            '//dl[@id="info-reel"]//span[text()="BEDROOMS"]/../../dd//span/p/text()')
    except:
        details['number_of_bedrooms'] = "N/A"

    try:
        details['number_of_bathrooms'] = tree.xpath(
            '//dl[@id="info-reel"]//span[text()="BATHROOMS"]/../../dd//span/p/text()')
    except:
        details['number_of_bathrooms'] = "N/A"

    try:
        details['property_size'] = tree.xpath('//dl[@id="info-reel"]//span[text()="SIZE"]/../../dd//span/p/text()')
    except:
        details['property_size'] = "N/A"

    try:
        details['tenure'] = tree.xpath('//dl[@id="info-reel"]//span[text()="TENURE"]/../../dd//span/p/text()')
    except:
        details['tenure'] = "N/A"

    try:
        details['council_tax'] = tree.xpath('//dt[text()="COUNCIL TAX"]/../dd/text()')
    except:
        details['council_tax'] = "N/A"

    try:
        details['parking'] = tree.xpath('//dt[text()="PARKING"]/../dd/span/text()')
    except:
        details['parking'] = "N/A"

    try:
        details['garden'] = tree.xpath('//dt[text()="GARDEN"]/../dd/span/text()')
    except:
        details['garden'] = "N/A"

    try:
        details['accessibilty'] = tree.xpath('//dt[text()="ACCESSIBILITY"]/../dd/span/text()')
    except:
        details['accessibilty'] = "N/A"

    try:
        details['stations'] = tree.xpath('//div[@id="Stations-panel"]//li//span/text()')
    except:
        details['stations'] = "N/A"
    return details


if __name__ == "__main__":

    total_listings = []
    total_pages_count = 42
    current_page_count = 0

    base_url = ("https://www.rightmove.co.uk/property-for-sale/find.html?propertyTypes=&includeSSTC=false&mustHave"
                "=&dontShow=&furnishTypes=&keywords=")

    url_location_hackney = f"{base_url}&locationIdentifier=REGION%5E61417"
    url_location_tower_hamlet = f"{base_url}&locationIdentifier=REGION%5E93953"
    url_location_camden = f"{base_url}&locationIdentifier=REGION%5E93941"
    url_location_ealing = f"{base_url}&locationIdentifier=REGION%5E93947"
    url_location_richmond = f"{base_url}&locationIdentifier=REGION%5E61415"

    # URL of the Rightmove page to scrape
    urls = [url_location_hackney, url_location_tower_hamlet, url_location_camden, url_location_ealing,
            url_location_richmond]

    for url in urls:
        current_page_count = 0
        # Fetch the listing
        while current_page_count < total_pages_count:
            new_url = url if current_page_count == 0 else f"{url}&index={current_page_count * 24}"
            listings = fetch_rightmove_listings(new_url)
            total_listings += listings
            current_page_count += 1

    df = pd.DataFrame(total_listings)
    df.to_csv("raw_data_file.csv", index=False)
    print("Scraping completed and data saved to raw_data_file.csv")
