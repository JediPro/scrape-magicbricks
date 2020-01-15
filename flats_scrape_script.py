"""
Code to scrape all results from magicbricks for a particular city.
This script dynamically searches for all flats for rent available in Mumbai, India
as on the time of execution of the script for properties ranging in size from 1 bedroom to 5 bedrooms,
and prices ranging from INR 1000 to INR 1000000.
It then scrapes 23 different information fields from each result, 
cleans the final data set and stores it to disk

Warning: Can take more than a day to run depending on internet speeds and RAM

@author: JediPro

"""
#%% Set environment
# Import libraries
import time
import pandas as pd
import os
from selenium import webdriver
import re
import sys
import numpy as np
import glob

# Set working directory here
wkdir = '../working_directory'
os.chdir(wkdir)

#%% Set chrome driver options
# Disable image loading
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

#%% Get list of options avaiable for budget ranges
'''
The website allows us to set any value in the url for min and max budget. Lets make use of that
We define a range from 1,000 to 1,000,000
Since prices increase exponentially, we define a series of numbers between 3 to 6
increasing by 0.1, then take 10 to that power to get final values
'''
t0_sect = time.time()

# Get exponential range
exp_range = list(np.arange(start=3, stop=6.1, step=0.1))
# Round above numbers to 2 decimals
exp_range = [np.round(a=num, decimals=2) for num in exp_range]
# Raise 10 to each number as power
budget_range = [int(np.round(a=10.0**num,decimals=0)) for num in exp_range]
# Set cityname
city_name = 'Mumbai'

# Create list of bedroom numbers
bedroom_range = list(range(1, 6))

# Create empty list to store urls
url_list = []
# Generate list of urls
for m in bedroom_range:
    for n in range(len(budget_range) - 1):
        
        # Generate url
        generated_url = ''.join(['https://www.magicbricks.com/property-for-rent/residential-real-estate?bedroom=',
                                str(m),
                                '&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Service-Apartment&cityName=', 
                                city_name,
                                '&BudgetMin=',
                                str(budget_range[n]),
                                '&BudgetMax=',
                                str(budget_range[n + 1] + 1)])
        # Append to list
        url_list.append(generated_url)
        
print('URL setup completed in',
      np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')

#%% Loop over each url and write results

# Define function
for j in range(len(url_list)):
    
    # j = 1
    
    # If there is an existing driver, close it
    if 'driver' in globals():
        driver.close()
    
    # Store url
    url = url_list[j]
    
    # Load webdriver for Chrome
    print('/n ###########-------------------#############/n')
    print('Loading web page for url no.', j + 1, '...')
    t0_sect = time.time()
    
    try:
        # Define driver
        driver = webdriver.Chrome(options=chrome_options)
        # Load website
        driver.get(url=url)
    except:
        continue
        
    print('Page loaded in:', 
          np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
    
    # Get count of results
    try:
        result_count = driver.find_element_by_xpath(
            xpath='//a[@class="active"]/span').text
        # Convert to int
        result_count = int(re.findall(pattern=r'[0-9]+', string=result_count)[0])
    except:
        continue
    
    
    # Print number of results found
    print(result_count, 'results present on page for current url')
    
    # Each page loads 30 results so divide by 30 to get page count
    page_count = np.floor(result_count/30)
    
    # Get page length
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    # Create flag to determine how long to run script
    match = False
    # Create counter to count number of scrolls
    scroll_num = 0
    # Keep scrolling until we reach end of page
    print('Scrolling page...')
    t0_sect = time.time()
    
    # Keep scrolling page until page height becomes constant or timeout occurs
    while(match == False):
        
        # Get current length of page
        lastCount = lenOfPage
        # Sleep for one second after each scroll to give data time to load
        time.sleep(2)
        
        # Scroll to end of page
        try:
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        except:
            print('Final scroll count: ' + str(scroll_num))
            print('Page scrolling completed in:', 
                  np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
            break
        
        # Update scroll_counter by 1
        scroll_num = scroll_num + 1
        # Print status every 10 scrolls
        if (scroll_num % 10) == 0:
            print(scroll_num, 'scrolls completed in',
                  np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
        # Check if new page length is the same as old one. If yes, break
        if lastCount == lenOfPage:
            print('Final scroll count: ' + str(scroll_num))
            print('Page scrolling completed in:', 
                  np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
            match = True

    # Extract the various elements
    
    # Extract location of all result cards
    t0_sect = time.time()
    
    div_results = driver.find_elements_by_xpath(
        xpath='.//span[@class="domcache js-domcache-srpgtm"]')
    # Print number of results located
    print(len(div_results), 'results located in',
          np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
    
    # Create empty list to store results
    prop_list = []

    # Now to loop over each element
    print('Looping over every web element...')
    t0_sect = time.time()
    
    for i in range(len(div_results)):
        
        # i = 1
        # Print status every 100th iteration
        if i % 20 == 0:
            print(i, 'results scraped in', 
                  np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
        
        # Pluck first element of result set
        try:
            elem_1 = div_results[i]
        except:
            continue
        
        # Create a blank dict
        prop_dict = {}
        
        # Get prop id
        try:
            prop_dict['id'] = elem_1.get_attribute(name='data-objid')
        except:
            prop_dict['id'] = np.nan
            
        # Get prop id string
        try:
            prop_dict['id_string'] = elem_1.get_attribute(name='id')
        except:
            prop_dict['id_string'] = np.nan
        
        # Get city name
        try:
            prop_dict['city'] = elem_1.get_attribute(name='data-cityname')
        except:
            prop_dict['city'] = np.nan
            
        # Get locality
        try:
            prop_dict['locality'] = elem_1.get_attribute(name='data-objlmtdname')
        except:
            prop_dict['locality'] = np.nan
        
        # Get poster name
        try:
            prop_dict['poster_name'] = elem_1.get_attribute(name='data-soname')
        except:
            prop_dict['poster_name'] = np.nan
            
        # Get property longitude
        try:
            prop_dict['longitude'] = driver.find_element_by_xpath(
                xpath='.//input[@id="pmtLong' + prop_dict['id'] + '"]'
                ).get_attribute(name='value')
        except:
            prop_dict['longitude'] = np.nan
        
        # Get property latitude
        try:
            prop_dict['latitude'] = driver.find_element_by_xpath(
                xpath='.//input[@id="pmtLat' + prop_dict['id'] + '"]'
                ).get_attribute(name='value')
        except:
            prop_dict['latitude'] = np.nan
        
        # Get element with info set 2
        try:
            elem_2 = driver.find_element_by_xpath(
                xpath='.//div[@data-id="' + prop_dict['id'] + '"]')
        except:
            continue
        
        # Get property title
        try:
            prop_dict['title'] = elem_2.find_element_by_xpath(
                xpath='.//meta[@itemprop="name"]').get_attribute(name='content')
        except:
            prop_dict['title'] = np.nan
        
        # Get property description
        try:
            prop_dict['desc'] = elem_2.find_element_by_xpath(
                xpath='.//meta[@itemprop="description"]').get_attribute(name='content')
        except:
            prop_dict['desc'] = np.nan
        
        # Get ad url
        try:
            prop_dict['url'] =  elem_2.find_element_by_xpath(
                xpath='.//meta[@itemprop="url"]').get_attribute(name='content')
        except:
            prop_dict['url'] = np.nan
            
        # Get property area
        try:
            prop_dict['area'] = elem_2.find_element_by_xpath(
                xpath='.//meta[@itemprop="floorSize"]').get_attribute(name='content')
        except:
            prop_dict['area'] = np.nan
        
        # Get Web element for info set 3
        try:
            elem_3 = elem_2.find_element_by_xpath(
                xpath='.//span[@id="' + prop_dict['id_string'] + '"]')
        except:
            continue
        
        # Get transaction type
        try:
            prop_dict['trans'] = elem_3.get_attribute(name='data-transactiontype')
        except:
            prop_dict['trans'] = np.nan
        
        # Get furnishing status
        try:
            prop_dict['furnishing'] = elem_3.get_attribute(name='data-furnshingstatus')
        except:
            prop_dict['furnishing'] = np.nan
        
        # Get floor number
        try:
            prop_dict['floor_num'] = elem_3.get_attribute(name='data-floorno')
        except:
            prop_dict['floor_num'] = np.nan
        
        # Get usertype
        try:
            prop_dict['user_type'] = elem_3.get_attribute(name='data-usertype')
        except:
            prop_dict['user_type'] = np.nan
    
        # Get number of bathrooms
        try:
            prop_dict['bathroom_num'] = elem_3.get_attribute(name='data-bathroom')
        except:
            prop_dict['bathroom_num'] = np.nan
        
        # Get number of bedrooms
        try:
            prop_dict['bedroom_num'] = elem_3.get_attribute(name='data-bedroom')
        except:
            prop_dict['bedroom_num'] = np.nan
        
        # Get developer name
        try:
            prop_dict['dev_name'] = elem_3.get_attribute(name='data-devname')
        except:
            prop_dict['dev_name'] = np.nan
        
        # Get project name
        try:
            prop_dict['project'] = elem_3.get_attribute(name='data-projectname')
        except:
            prop_dict['project'] = np.nan
        
        # Get ad posting date
        try:
            prop_dict['post_date'] = elem_3.get_attribute(name='data-createdate')
        except:
            prop_dict['post_date'] = np.nan
        
        # Get property type
        try:
            prop_dict['type'] = elem_3.get_attribute(name='data-propertyval')
        except:
            prop_dict['type'] = np.nan
        
        # Get price
        try:
            prop_dict['price'] = elem_3.get_attribute(name='data-price')
        except:
            prop_dict['price'] = np.nan
        
        # Get all child summary elements
        try:
            elem_4_summ_item = elem_2.find_element_by_xpath(
                xpath='.//div[@class="m-srp-card__summary js-collapse__content"]/div[@class="m-srp-card__summary__item"]')
        except:
            continue
    
        # Extract item title
        try:
            item_title = elem_4_summ_item.find_element_by_xpath(
                xpath = './/div[@class="m-srp-card__summary__title"]').text
        except:
            item_title = np.nan
        
        # If above title is 'FLOOR', then extract info and store else keep blank
        if item_title == 'FLOOR':
            try:
                prop_dict['floor_count'] = elem_4_summ_item.find_element_by_xpath(
                    xpath = './/div[@class="m-srp-card__summary__info"]').text
            except:
                prop_dict['floor_count'] = np.nan
        else:
            prop_dict['floor_count'] = np.nan
        
        # Add current dict to list
        prop_list.append(prop_dict)
        
        # Store final count of results
        final_count = i
    
    # Convert dict to data frame
    prop_df = pd.DataFrame(prop_list)
    # Write to disk with sequence number in name
    prop_df.to_csv(path_or_buf= ''.join(['property_data_', 
                                         str(j + 1), '.csv']), index=False)
    
    print(final_count + 1, 'results scraped for url number', j + 1, 'in', 
      np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')

#%% Load all written data files
print('Loading all data files...')
t0_sect = time.time()
    
# Load list of all data files that have the string 'property_data'
try:
    property_files = glob.glob(pathname = wkdir + '/property_data*.csv')
    # Read all files and store in list
    data_list = [pd.read_csv(file) for file in property_files]
    # concatenate all data frame
    full_prop_data = pd.concat(data_list, ignore_index=True)
except:
    sys.exit('Data files could not be loaded')

print('Data files loaded in', 
      np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
# Print data sumamry
print('The full data has', 
      full_prop_data.shape[0], 'rows and', 
      full_prop_data.shape[1], 'columns')

#%% Process data
print('Processing data...')
t0_sect = time.time()

try:
    # Get counts of non NAs in each column
    print(full_prop_data.count())
    '''
    We see that the columns area, bathroom_num, desc, dev_name, floor_count, 
    floor_num, furnishing, locality, poster_name, project, title, trans, url
    all have NA values
    '''
    
    # Since ID column has no NAs, we remove duplicates from the data frame using the same
    full_prop_data = full_prop_data.drop_duplicates(subset = 'id')
    # Print new count
    print('Dropping duplicates leaves us with', full_prop_data.shape[0], 'rows')
    
    # Process area column ---------------
    # Keep only numbers, convert to float
    full_prop_data['area'] = full_prop_data['area'].str.extract(pat=r'([0-9]*)').astype(float)
    # Process floor_count column ---------------
    # Keep max floors value
    full_prop_data['floor_count'] = full_prop_data['floor_count'].str.extract(
        pat=r'out of ([0-9]*) Floors').astype(float)
    # Process floor_num column ---------------
    # Three text values in the column, create a dict to map them to floor num
    floor_num_dict = {'Ground':'0', 'Upper Basement':'-1', 'Lower Basement':'-2'}
    # Map dict to column
    full_prop_data['floor_num'] = full_prop_data['floor_num'].replace(
        to_replace=floor_num_dict).astype(float)
    # Process post_date column ---------------
    # Convert to datetime object
    full_prop_data['post_date'] = pd.to_datetime(arg=full_prop_data['post_date'], 
                                                 format='%Y%m%d', errors='coerce')
    
    # Write data
    full_prop_data.to_csv('prop_data_clean.csv', index=False)
    
    print('Data processed and written in', 
          np.round(a = (time.time() - t0_sect)/60, decimals=2), 'm')
except:
    sys.exit('Data could not be processed')












