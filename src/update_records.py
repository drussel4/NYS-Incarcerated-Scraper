from airtable_api import getParticipants, setParticipantData
from scraper import scrape

def check_addresses(databased_dict, scraped_dict):

    print('Beginning check_addresses()')

    databased_dict = getParticipants()
    dins = []
    for record in databased_dict['records'].keys():
        dins.append(record['fields']['DIN'])
    scraped_dict = scrape(dins)

    update_list = {}
    tracker = {'checked':0, 'updated':0, 'error':0}
    for record in databased_dict['records'].keys():
        din = record['fields']['DIN']
        print('Beginning status check for participant {} with DIN {}'.format(record['id'], record['fields']['DIN']))
        if din not in scraped_dict.keys():
            print('Weird, did not find DIN: {} in scraped_dict. Was that an error?'.format(din))
            tracker['error'] += 1
        else:
            if record['fields']['Address'] == scraped_dict[din]['address']:
                print('Match between AirTable ({}) and NYS website ({}), no update required'.format(
                    record['fields']['Address'], scraped_dict[din]['address']))
                tracker['checked'] += 1
            else:
                print('Mismatch between AirTable ({}) and NYS website ({}), updating AirTable!'.format(
                    record['fields']['Address'], scraped_dict[din]['address']))
                record['fields']['Address'] = scraped_dict[din]['address']
                update_list.append(record)
                tracker['checked'] += 1
                tracker['updated'] += 1
    
    print('Unable to find data for {} participants. For records found, {}/{} addresses required an update.'.format(
        tracker['error'], tracker['updated'], tracker['checked']))

    try:
        setParticipantData({'records':update_list})
        print('Successfully updated {} records with setParticipantData()'.format(tracker['updated']))
    except Exception as e:
        print('Failed to complete setParticipantData(), error:', e)
    
    print('Completed check_addresses()')
