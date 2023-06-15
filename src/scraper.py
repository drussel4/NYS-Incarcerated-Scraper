# Import packages
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import json

# Align driver and set options
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
DRIVER_PATH = '.\driver\chromedriver.exe'
service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=service)

dins = [
    '97A5705',
    '16A4309',
    '10A2667',
    ]

def test_function(dins):

    website = 'https://nysdoccslookup.doccs.ny.gov/'
    xpaths = {
        'input':'//*[@id="din"]',
        'search':'/html/body/app/div[1]/div/div[3]/div[3]/form/div[2]/div[2]/div/button[1]',
        'name':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[1]/div/h3',
        'custody':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[5]/div[2]',
        'facility':'/html/body/app/div[1]/div/div[3]/div[4]/div[2]/div[1]/div/div[6]/div[2]'
        }
    results = {}
    for d in dins:
        d_dict = {}
        driver.get(website)
        sleeper = 5
        print('About to pause for {} second(s)...'.format(sleeper))
        time.sleep(sleeper)
        driver.find_element(By.XPATH, xpaths['input']).send_keys(d)
        driver.find_element(By.XPATH, xpaths['search']).click()
        time.sleep(1)

        # Retrieve elements
        for k in ['name', 'custody', 'facility']:
            d_dict[k] = driver.find_element(By.XPATH, xpaths[k]).text
        
        # Store elements per DIN
        results[d] = d_dict
    
    print('Finished scraping!')
    with open('results.json', 'w') as fp:
        json.dump(results, fp, default=str)

test_function(dins)
