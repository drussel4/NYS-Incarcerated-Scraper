import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Align driver and set options
options = webdriver.ChromeOptions()
# if os.environ.get('CI', False):
options.add_argument('--headless=new')
options.add_argument('--start-maximized')
chrome_version = '116.0.5845.96'
driver = webdriver.Chrome(service=ChromeService(version=chrome_version), options=options)

def scrape(dins):
    
    print('Beginning scrape()')

    website = 'https://nysdoccslookup.doccs.ny.gov'
    xpaths = {
        'input':'//*[@id="din"]',
        'search':'/html/body/app/div[1]/div/div[3]/div[3]/form/div[2]/div[2]/div/button[1]',
        'Name':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[1]/div/h3',
        'Custody':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[5]/div[2]',
        'Facility':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[6]/div[2]'
        }
    scraped_dict = {}
    sleeper = (2, 0.5)
    processing_time = len(dins)*(sleeper[0]+sleeper[1])
    print('About to fetch data for {} DINs. Expected to take scraper ~{} seconds...'.format(len(dins), processing_time))
    # counter = 0
    for d in dins:

        if len(d) == 0:
            continue
        
        # Temporary limit for testing purposes
        # counter += 1
        # if counter >= 13:
        #     break

        d_dict = {}
        driver.get(website)
        # print('Pausing for {} seconds...'.format(sleeper[0]))
        time.sleep(sleeper[0])
        driver.find_element(By.XPATH, xpaths['input']).send_keys(d)
        driver.find_element(By.XPATH, xpaths['search']).click()
        time.sleep(sleeper[1])

        # Retrieve elements
        for k in ['Name', 'Custody', 'Facility']:
            d_dict[k] = driver.find_element(By.XPATH, xpaths[k]).text

        # Store elements per DIN
        scraped_dict[d] = d_dict
    
    # with open('scraped_dict.json', 'w') as fp:
    #     json.dump(scraped_dict, fp, default=str)

    print('Completed scrape(), fetched data for {} DINs'.format(len(scraped_dict.keys())))
    
    return scraped_dict

def facilities_scrape():
    
    print('Beginning facilities_scrape()')

    website = 'https://doccs.ny.gov/facilities'
    facility_div = 'webny-teaser-title'
    detail_divs = {
        'Counties':'location-counties',
        'Address1':'address-line1',
        'Address2':'address-line2',
        'City':'locality',
        'State':'administrative-area',
        'ZIP':'postal-code',
        }
    driver.get(website)
    sleeper = 5
    print('Pausing for {} seconds...'.format(sleeper))
    time.sleep(sleeper)
    total_counter = 0
    facilities_dict = {}
    for page in range(0, 99):
    # for page in range(2, 3):
        driver.get('{}?page={}'.format(website, page))
        sleeper = 2
        print('Paged forward, pausing for {} seconds...'.format(sleeper))
        results = driver.find_elements(By.CLASS_NAME, facility_div)
        if len(results) == 0:
            print('Found no elements, finished!')
            break
        else:
            print('Found {} elements, continuing...'.format(len(results)))
            inner_counter = 0
            for r in results:
                results = driver.find_elements(By.CLASS_NAME, facility_div)
                facility_name = results[inner_counter].text
                facility_url = 'https://doccs.ny.gov/location/{}'.format(facility_name.lower().replace(' ', '-'))
                facility_dict = {
                    'Name':facility_name,
                    'URL':facility_url,
                    }
                driver.get(facility_url)
                time.sleep(sleeper)
                for k in detail_divs.keys():
                    try:
                        facility_dict[k] = driver.find_element(By.CLASS_NAME, detail_divs[k]).text
                    except Exception as e:
                        # print('Failed to get "{}" for {}, error: {}'.format(k, facility_dict['Name'], e))
                        facility_dict[k] = None
                
                short_name = ''
                for long_name in ['Residential Treatment Facility', 'Correctional Facility']:
                    short_name = facility_name.replace(long_name, '')
                short_name = short_name.strip().upper()
                facility_dict['Short Name'] = short_name
                facilities_dict[short_name] = facility_dict
                inner_counter += 1
                total_counter += 1
                print('Through {} facilities on page, {} overall...'.format(inner_counter, total_counter))
                
                # Navigate to list
                driver.get('{}?page={}'.format(website, page))
                time.sleep(sleeper)
    
    # with open('facilities_dict.json', 'w') as fp:
    #     json.dump(facilities_dict, fp, default=str)
    
    print('Completed facilities_scrape(), fetched data for {} facilities'.format(len(facilities_dict.keys())))

    return facilities_dict
