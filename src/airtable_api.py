import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

api_key=os.environ.get('AIRTABLE_API_KEY')
airtable_base_url = 'https://api.airtable.com/v0/appw8RcYW8sB8Br2E'
headers = {'Authorization':'Bearer {}'.format(api_key)}

# Query for list of participants, including DIN
def getParticipants():

    # Request
    print('Running getParticipants()')

    # Send request
    data_url = '{}/{}'.format(airtable_base_url, 'Official%20Program%20Participants')
    response = requests.get(data_url, headers=headers)
    print('response:', response)
    data = response.json()

    with open('data.json', 'w') as fp:
        json.dump(data, fp, default=str)
    
    # din_to_address_dict = {}
    # for record in data['records']:
    #     din_to_address_dict[record['fields']['DIN']] = record['fields']['Address']
    
    return data

# getParticipants()

def setParticipantData(update_dict):

    # Request
    print('Running setParticipantData()')

    # Add to headers
    headers['content-type'] = 'application/json'

    print('Intentionally cutting setParticipantData() off early in order to not incidentally overwrite data')
    return

    # Send request
    data_url = '{}/{}'.format(airtable_base_url, 'Official%20Program%20Participants')
    response = requests.patch(data_url, headers=headers, params=update_dict)
    print(response)
    
    return

# setParticipantData()

### SAMPLE
#   "records": [
#     {
#       "id": "recdx1YtFqKyYaYlb",
#       "fields": {
#         "First Name": "Raymond",
#         "Last Name": "Warren",
#         "DIN": "98A0452",
#         "Address": "GREEN HAVEN CORRECTIONAL FACILITY, 594 Rt. 216",
#         "address_city": "STORMVILLE",
#         "address_state": "NY",
#         "address_zip": "12582-0010"
#       }
#     },
#     {
#       "id": "rec33KfQmaQoTOS8V",
#       "fields": {
#         "First Name": "Leperry",
#         "Last Name": "Fore",
#         "DIN": "03A0270",
#         "Address": "FISHKILL CORRECTIONAL FACILITY, 271 Matteawan Road, P.O. Box 1245",
#         "address_city": "BEACON",
#         "address_state": "NY",
#         "address_zip": "12508-0307"
#       }
#     },
#     {
#       "id": "recL0CuIALLOVwyy8",
#       "fields": {
#         "First Name": "Anthony",
#         "Last Name": "Perez",
#         "DIN": "06A1261",
#         "Address": "SING SING CORRECTIONAL FACILITY, 354 Hunter Street",
#         "address_city": "OSSINING",
#         "address_state": "NY",
#         "address_zip": "10562-5442"
#       }
#     }
#   ]
# }'
