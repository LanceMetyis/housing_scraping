import requests
from bs4 import BeautifulSoup


def fetch_rightmove_listings(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all property listings
    listings = soup.find_all('div', attrs={'class': 'propertyCard'})
    listings+=  soup.find_all('div', attrs={'class': 'property-info'})
    print("found")

    # Extract and print details for each listing
    properties = []
    for listing in listings:
        try:
            title = listing.find('h2', class_='propertyCard-title').text.strip()
            address = listing.find('address', class_='propertyCard-address').text.strip()
            price = listing.find('div', class_='propertyCard-priceValue').text.strip()
            link = listing.find('a', class_='propertyCard-link')['href']
            full_link = f"https://www.rightmove.co.uk{link}"
            property_type= listing.find('span', class_ ='text').text.strip()

            property_details = {'title': title, 'address': address, 'price': price, 'link': full_link,
                                'propertyType': property_type, }

            properties.append(property_details)

        except AttributeError as e:
            # Handle cases where some details might not be present in the listing
            print(f"Error extracting details for a listing: {e}")
            continue

    return properties


# URL of the Rightmove page to scrape
url = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93917'

# Fetch the listings
listings = fetch_rightmove_listings(url)

# Print the results
for property in listings:
    print(f"Title: {property['title']}")
    print(f"Address: {property['address']}")
    print(f"Price: {property['price']}")
    print(f"Link: {property['link']}")
    print(f"Property Type: {property['propertyType']}")
    print("-----")