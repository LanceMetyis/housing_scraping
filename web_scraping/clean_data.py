import pandas as pd
import numpy as np
import re
from decimal import Decimal
from datetime import datetime, timedelta

#read raw data file
df = pd.read_csv('raw_data_file.csv')


# get unique rows
def extract_property_id(url):
    parts = url.split('/')
    property_id = parts[-2][:-1]
    return property_id


df['property_id'] = df['link'].apply(extract_property_id)
# drop unwanted columns
del df['title']
del df['accessibilty']
del df['agentContactNumber']
del df['description']
del df['link']

# removing special characters from property type, bedrooms, bathrooms, size, tenure, council_tax, parking, garden,
# accessibility, stations
extra_chars = ["[", "]", "'"]
for char in extra_chars:
    df['property_type'] = df['property_type'].str.replace(char, '')
    df['number_of_bedrooms'] = df['number_of_bedrooms'].str.replace(char, '')
    df['number_of_bathrooms'] = df['number_of_bathrooms'].str.replace(char, '')
    df['property_size'] = df['property_size'].str.replace(char, '')
    df['tenure'] = df['tenure'].str.replace(char, '')
    df['council_tax'] = df['council_tax'].str.replace(char, '')
    df['parking'] = df['parking'].str.replace(char, '')
    df['garden'] = df['garden'].str.replace(char, '')
    df['stations'] = df['stations'].str.replace(char, '')

# Updating 'Ask agent', 'TBC', 'Ask Developer' to blank
inputs = ["Ask agent", "TBC", "Ask developer", "NaN"]
for value in inputs:
    df['tenure'] = df['tenure'].str.replace(value, '0')
    df['council_tax'] = df['council_tax'].str.replace(value, '0')
    df['parking'] = df['parking'].str.replace(value, '')
    df['garden'] = df['garden'].str.replace(value, '')
    df['property_size'] = df['property_size'].str.replace(value, '')

# Cleaning agencyDetails column
df['agencyDetails'] = df['agencyDetails'].str.slice(2)

# Cleaning council tax column
df.loc[df['council_tax'].str.contains('Band'), 'council_tax'] = df['council_tax'].str.slice(6)

# Remove text and change the date format from addedOn column
df['addedOn'] = df['addedOn'].str.split(' ').str[-1]

# replacing today's and yesterday's date with actual date
today = datetime.now().strftime('%d/%m/%Y')
yesterday = (datetime.now() - timedelta(1)).strftime('%d/%m/%Y')
for index, row in enumerate(df['addedOn']):
    if row == 'today':
        df.loc[index, 'addedOn'] = today
    elif row == 'yesterday':
        df.loc[index, 'addedOn'] = yesterday

# change date time format
df['addedOn'] = pd.to_datetime(df['addedOn'], dayfirst=True)

# Cleaning price column
df['price'] = df['price'].replace('[\£\,\,.]', '', regex=True).astype(int)

# updating garden entries in BOOLEAN values
for index, row in enumerate(df['garden']):
    if len(row) == 0 or 'No' in row:
        df.loc[index, 'garden'] = False
    else:
        df.loc[index, 'garden'] = True

# updating parking entries in BOOLEAN values
for index, row in enumerate(df['parking']):
    if len(row) == 0 or 'No' in row:
        df.loc[index, 'parking'] = False
    else:
        df.loc[index, 'parking'] = True

# Cleaning agency address from df['agencyDetails]
df['agencyDetails'] = df['agencyDetails'].str.split(',').str[0]

# Updating stations column with the nearest distance calculated
df['stations'] = df['stations'].str.split(',')
for index, row in enumerate(df['stations']):
    stations_per_miles_list = []
    for element in row:
        if "miles" in element:
            element = element.replace('miles', '')
            stations_per_miles_list.append(Decimal(element))
    stations_per_miles_list.sort()
    df.loc[index, 'stations'].clear()
    df.loc[index, 'stations'].extend(stations_per_miles_list)
    stations_per_miles_list.clear()

df['stations'] = df['stations'].str[0]


# Cleaning property size column
def extract_sq_m(input_string):
    match = re.search(r'(\d+(?:,\d+)*)\s*sq\s*m', input_string)
    if match:
        return int(match.group(1).replace(',', ''))
    return None


for index, row in enumerate(df['property_size']):
    df.loc[index, 'property_size'] = extract_sq_m(row)

# Cleaning full address to postcode
df['address'] = df['address'].str.split(',').str[-1].str.strip()
for index, row in enumerate(df['address']):
    check_postcode = False
    for char in row:
        if char.isdigit():
            check_postcode = True
            break
        check_postcode = False
    if check_postcode:
        df.loc[index, 'address'] = row
    else:
        df.loc[index, 'address'] = 'NA'

# getting postcode initials
df['address'] = df['address'].str.split(' ')
for index, row in enumerate(df['address']):
    post_code = []
    for element in row:
        if not element.isalpha() and not element.isdigit():
            post_code.append(element)
    df.loc[index, 'address'].clear()
    if len(post_code) == 0:
        df.loc[index, 'address'] = 0
    else:
        df.loc[index, 'address'] = post_code[0]
    post_code.clear()

# Droping property_type as 'Plot'
df.drop(df[df['property_type'] == 'Plot'].index, inplace=True)

# Droping empty rows
df.drop(df[(df['property_type'] == "") | (df['number_of_bathrooms'] == "") | (df['number_of_bedrooms'] == "") | (
        df['address'] == "")].index, inplace=True)

# Updating blank property size entries with avg value
df_mean_values = df.dropna(subset=['property_size'])
total_property_size = df_mean_values['property_size'].sum()
total_bedrooms = pd.to_numeric(df_mean_values['number_of_bedrooms']).sum()
average_property_size_value = int(total_property_size / int(total_bedrooms))
df['property_size'].fillna(average_property_size_value * pd.to_numeric(df['number_of_bedrooms']), inplace=True)

# reindexing the index
df.index = np.arange(1, len(df) + 1)

# Rename columns
df.rename(
    columns={'property_type': 'Property Type', 'number_of_bedrooms': 'Bedrooms', 'number_of_bathrooms': 'Bathrooms',
             'property_size': 'Floor Area', 'tenure': 'Tenure', 'council_tax': 'Council Tax Band', 'parking': 'Parking',
             'garden': 'Garden', 'stations': 'Distance From Nearest Station', 'address': 'Postcode',
             'agencyDetails': 'Marketed By', 'property_id': 'Property ID', 'addedOn': 'Published Date',
             'price': 'Price'}, inplace=True)

# reordering columns
df = df.reindex(
    ['Property ID', 'Property Type', 'Bedrooms', 'Bathrooms', 'Floor Area', 'Postcode', 'Published Date', 'Price',
     'Tenure', 'Council Tax Band', 'Parking', 'Garden', 'Distance From Nearest Station', 'Marketed By'], axis=1)

# drop duplicates
df.drop_duplicates(subset=['Property ID'], inplace=True)

# save the dataframe to csv
df.to_csv('cleaned_data_set.csv', mode='w+', index=False)

print("Cleaned data successfully!!")
