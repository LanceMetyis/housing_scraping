from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E93917"
driver.get(url)

time.sleep(3)

property_cards = driver.find_elements(By.CLASS_NAME, "propertyCard-img-link")

property_details = []

for card in property_cards:
    try:
        card.click()
        time.sleep(3)  
        
        # Extract property details
        try:
            address = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[2]/div/div[1]/div[1]/div/h1').text
        except:
            address = "N/A"

        try:
            price = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[2]/div/article[1]/div/div/div[1]/span[1]').text
        except:
            price = "N/A"

        try:
            property_type = driver.find_element(By.XPATH, '//*[@id="info-reel"]/div[1]/dd/span/p').text
        except:
            property_type = "N/A"

        try:
            bedrooms = driver.find_element(By.XPATH, '//*[@id="info-reel"]/div[2]/dd/span/p').text
        except:
            bedrooms = "N/A"

        try:
            bathrooms = driver.find_element(By.XPATH, '//*[@id="info-reel"]/div[3]/dd/span/p').text
        except:
            bathrooms = "N/A"

        try:
            size = driver.find_element(By.XPATH, '//*[@id="info-reel"]/div[4]/dd/span/p[1]').text
        except:
            size = "N/A"

        try:
            tenure = driver.find_element(By.XPATH, '//*[@id="info-reel"]/div[5]/dd/span/p').text
        except:
            tenure = "N/A"

        try:
            description = driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[2]/div/article[3]/div[3]/div/div').text
        except:
            description = "N/A"
        
        # Append the details to the list
        property_details.append({
            "Address": address,
            "Price": price,
            "Property Type": property_type,
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Size": size,
            "Tenure": tenure,
            "Description": description
        })
        
        # Navigate back to the main page
        driver.back()
        time.sleep(3)  

        property_cards = driver.find_elements(By.CLASS_NAME, "propertyCard-img-link")
    except Exception as e:
        print(f"An error occurred: {e}")

driver.quit()

df = pd.DataFrame(property_details)
df.to_csv("property_details.csv", index=False)
print("Scraping completed and data saved to property_details.csv")
