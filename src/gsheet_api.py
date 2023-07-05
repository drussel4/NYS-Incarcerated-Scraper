import os.path
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from dotenv import load_dotenv
load_dotenv()

gsheet_creds=os.environ.get('GOOGLE_APP_CREDENTIALS_JSON')
sheet_id=os.environ.get('GSHEET_ID')

# Calls Google Sheets API
def getData():

    print('Beginning getData()')

    # Establish credentials from service account
    service_account_info = json.loads(gsheet_creds)
    creds = service_account.Credentials.from_service_account_info(service_account_info)
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    worbook = sheet.get(spreadsheetId=sheet_id).execute()
    sheets = worbook['sheets']
    first_sheet = sheets[0]
    result = sheet.values().get(
        spreadsheetId=sheet_id,
        range=first_sheet['properties']['title'],
        majorDimension='ROWS'
    ).execute()
    values = result.get('values', None)
    
    # with open('values.json', 'w') as fp:
    #     json.dump(values, fp, default=str)
    
    # Store results in dictionary with DIN as primary key
    gsheet_dict = {}
    if not values:
        raise Exception('No data found...')
    else:
        headers = values[0]
        label_indexes = {}
        for h in headers:
            label_indexes[h] = headers.index(h)
        try:
            din_index = label_indexes['DIN']
            status_index = label_indexes['Status']
            print('Found DIN and Status columns in positions {} and {}, respectively:'.format(din_index, status_index))
        except:
            raise Exception('Unable to find 1+ or required columns "DIN" and "Status", cannot proceed...')
        for row in values[1:]:
            if len(row) < max(din_index, status_index):
                continue
            if row[status_index].lower().strip() == 'released':
                continue
            gsheet_dict[row[din_index]] = dict(zip(headers, row))
    
    # with open('gsheet_dict.json', 'w') as fp:
    #     json.dump(gsheet_dict, fp, default=str)
    
    return gsheet_dict

# getData()
