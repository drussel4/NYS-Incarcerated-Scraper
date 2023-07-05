from airtable_api import setParticipantData, createTable
from gsheet_api import getData
from scraper import scrape, facilities_scrape
from emailer import send_email
import json

# Check whether custody status has changed
def compare(gsheet_dict, scraped_dict, facilities_dict):

    print('Beginning compare()')

    compare_dict = {'Changed':[], 'Unchanged':[]}
    for din in gsheet_dict.keys():
        if din in scraped_dict.keys():
            changed = []
            d = scraped_dict[din].copy()
            d['DIN'] = din
            d['Changes'] = None

            ### Check custody status
            if scraped_dict[din]['Custody'].replace('_', '').upper() != gsheet_dict[din]['Status'].replace('_', '').upper():
                changed.append('Custody')
            
            ### Check facility
            if scraped_dict[din]['Facility'] is not None and scraped_dict[din]['Facility'].upper() in facilities_dict.keys():
                print('Found matching facility!')
                facility_diff = False
                for field_tuple in [
                    ('To Mailing City', 'City'),
                    ('To Mailing State', 'State'),
                    ]:
                    if gsheet_dict[din][field_tuple[0]].upper() != facilities_dict[scraped_dict[din]['Facility'].upper()][field_tuple[1]].upper():
                        facility_diff = True
                        break
                for field_tuple in [('To Mailing ZIP', 'ZIP')]:
                    if gsheet_dict[din][field_tuple[0]][:5] != facilities_dict[scraped_dict[din]['Facility'].upper()][field_tuple[1]][:5]:
                        facility_diff = True
                if facility_diff == True:
                    changed.append('Facility')
            else:
                print('Unable to find matching facility for "{}" in facilities_dict.keys()...'.format(scraped_dict[din]['Facility'].upper()))

            if len(changed) > 0:
                d['Changes'] = ', '.join(changed)
                compare_dict['Changed'].append(d)
            else:
                compare_dict['Unchanged'].append(d)
    
    print('{}/{} participants have a custody status requiring an update'.format(len(compare_dict['Changed']), len(scraped_dict)))
    print('Completed compare()')

    # with open('compare_dict.json', 'w') as fp:
    #     json.dump(compare_dict, fp, default=str)

    return compare_dict

def job():

    print('Beginning job()')

    # Fetch data
    gsheet_dict = getData()
    scraped_dict = scrape(list(gsheet_dict.keys()))
    facilities_dict = facilities_scrape()
    # with open('scraped_dict.json') as json_file:
    #     scraped_dict = json.load(json_file)
    # with open('gsheet_dict.json') as json_file:
    #     gsheet_dict = json.load(json_file)
    # with open('facilities_dict.json') as json_file:
    #     facilities_dict = json.load(json_file)
    compare_dict = compare(gsheet_dict, scraped_dict, facilities_dict)
    
    # Orient list of dictionaries to POST to Airtable
    create_list = []
    for status in compare_dict.keys():
        for record in compare_dict[status]:
            record_dict = {
                'DIN':record['DIN'],
                'Name':record['Name'],
                'Custody':record['Custody'],
                'Facility':record['Facility'],
                'Flag':status,
                'Changes':record['Changes'],
            }
            create_list.append({'fields':record_dict})
    
    # Create table in base
    try:
        table_name = createTable()
        print('Successfully created table with name "{}"'.format(table_name))
    except Exception as e:
        print('Failed to created table, error:', e)
        raise e
    
    # POST records to new table
    try:
        setParticipantData(table_name, create_list)
        print('Successfully created {} records with setParticipantData()'.format(len(create_list)))
    except Exception as e:
        print('Failed to complete setParticipantData(), error:', e)
        raise e
    
    # Send email notifying of job completion
    try:
        send_email(compare_dict)
    except Exception as e:
        print('Failed to send email notifying of job completion, error:', e)
        raise e
    
    print('Completed job()')

if __name__ == '__main__':
    job()
