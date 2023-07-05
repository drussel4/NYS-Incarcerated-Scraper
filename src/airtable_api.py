import os
import requests
import json
import datetime as dt
from dateutil import tz
from dotenv import load_dotenv
load_dotenv()

api_key=os.environ.get('AIRTABLE_API_KEY')
access_token=os.environ.get('AIRTABLE_ACCESS_TOKEN')

# [DEPRECATED] Query for list of participants, including DIN
# NOTE: Switched method to read from GSheet instread
def getParticipants():

    # Request
    print('Running getParticipants()')

    # Set headers
    headers = {'Authorization':'Bearer {}'.format(api_key)}

    # Send request
    data_url = 'https://api.airtable.com/v0/{}/{}'.format(os.environ.get('AIRTABLE_READ_ID'), 'tbl01hfEt9e0EK0k9')
    response = requests.get(data_url, headers=headers)
    print('response:', response)
    if response.status_code != 200:
      raise Exception('getParticipants() failed with status code {}: {}'.format(response.status_code, response.text))
    data = response.json()

    # with open('data.json', 'w') as fp:
    #     json.dump(data, fp, default=str)
    
    return data

# Create new table in base
# NOTE: Airtable enforces unique table names
# NOTE: Convert forward slashes (e.g., 6/22/2023 >> 6%2F22%2F2023)
def createTable():

    # Request
    print('Running createTable()')

    # Set headers
    headers = {
        'Authorization':'Bearer {}'.format(access_token),
        'content-type':'application/json',
        }
    
    # Table name, today in ET (converted from UTC)
    today = dt.datetime.utcnow()
    utc_zone = tz.gettz('UTC')
    eastern_zone = tz.gettz('America/New_York')
    today = today.replace(tzinfo=utc_zone)
    today = today.astimezone(eastern_zone)
    today_str = today.strftime('%m/%d/%Y')
    print('Creating table with name:', today_str)

    # Table schema
    table_dict = {"fields": [
        {
            "name": "DIN",
            "type": "singleLineText"
          },
          {
            "name": "Name",
            "type": "singleLineText"
          },
          {
            "name": "Facility",
            "type": "singleLineText"
          },
          {
            "name": "Custody",
            "type": "singleLineText"
          },
          {
            "name": "Flag",
            "type": "singleLineText"
          },
          {
            "name": "Changes",
            "type": "singleLineText"
          },
          
        ],
        "name": today_str
      }
    
    # Send request
    data_url = 'https://api.airtable.com/v0/meta/bases/{}/tables'.format(os.environ.get('AIRTABLE_WRITE_ID'))
    response = requests.request('POST', data_url, headers=headers, data=json.dumps(table_dict))
    print('response:', response)
    if response.status_code != 200:
      raise Exception('createTable() failed with status code {}: {}'.format(response.status_code, response.text))
    
    return today_str

# Airtable requires POSTs to be in batches of maximum 10 records
def batch_records(create_list):

  batched = []
  batch_size = 10
  for i in range(0, len(create_list), batch_size): 
      batched.append(create_list[i:i + batch_size])
  
  # with open('batched.json', 'w') as fp:
  #     json.dump(batched, fp, default=str)
  
  return batched
   
# Write data to a specific table
def setParticipantData(table_name, create_list):

    # Request
    print('Running setParticipantData()')

    # Set headers
    headers = {
        'Authorization':'Bearer {}'.format(api_key),
        'content-type':'application/json',
        }
    
    # Prepate request
    table_name = table_name.replace('/', '%2F')
    data_url = 'https://api.airtable.com/v0/{}/{}'.format(os.environ.get('AIRTABLE_WRITE_ID'), table_name)

    # Batch records, if necessary
    if len(create_list) > 10:
       batches = batch_records(create_list)
       for batch in batches:
          response = requests.request('POST', data_url, headers=headers, data=json.dumps({'records':batch}))
    else:
      response = requests.request('POST', data_url, headers=headers, data=json.dumps({'records':create_list}))
      print('response:', response)
      if response.status_code != 200:
        raise Exception('setParticipantData() failed with status code {}: {}'.format(response.status_code, response.text))
      
    return response
