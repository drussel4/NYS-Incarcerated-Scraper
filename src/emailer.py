import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from dotenv import load_dotenv
load_dotenv()

# HTML and plain text handling for section headers
def write_section_header():
    headers = {}
    for header in ['Changed', 'Unchanged']:
        html = '<body style="border-bottom: 3px solid #5894B7;font-size:16px"><b>&nbsp;{}</b></body><br>'.format(header)
        headers[header] = {
            'html':html,
            'plain':header.upper()
        }
    return headers

# Craft body of email with participant details (DIN, facility, etc.)
def craft_message(compare_dict, image_cid):

    # Intro text (HTML)
    nys_hyperlink = 'https://airtable.com/appBE7gcXl07kScAA/tblUlJcll3UjNtjZn/viwg5WPzypb9n0Xnp?blocks=hide'
    airtable_hyperlink = 'https://airtable.com/appBE7gcXl07kScAA/tblUlJcll3UjNtjZn/viwg5WPzypb9n0Xnp?blocks=hide'
    html_intro_text = '''
    <body style="font-size:12px"><i>
    Data has been scraped from the NYS Department of Corrections and Community Supervision <a href="{}">website</a>. Visit <a href="{}">Airtable</a> to see the results.
    </i></body>
    '''.format(nys_hyperlink, airtable_hyperlink)

    # Intro text (plain text)
    plain_intro_text = 'Data has been scraped from the NYS Department of Corrections and Community Supervision website at {}. Visit Airtable at {} to see the results.'.format(nys_hyperlink, airtable_hyperlink)

    # Body text, participant details
    participants = {
        'Changed': {
            'html':'',
            'plain':'',
            },
        'Unchanged': {
            'html':'',
            'plain':'',
            },
        }
    for status in compare_dict.keys():
        for record in compare_dict[status]:

            # HTML
            participants[status]['html'] = participants[status]['html'] + '<body style="font-size:14px"><b>{} [{}]</b></body>'.format(record['Name'], record['DIN'])
            participants[status]['html'] = participants[status]['html'] + '<body style="font-size:12px"><i>{} | {}</i></body>'.format(record['Custody'], record['Facility'])
            if status == 'Changed':
                participants[status]['html'] = participants[status]['html'] + '<body style="font-size:12px">CHANGES: {}</body>'.format(record['Changes'])
            participants[status]['html'] = participants[status]['html'] + '<br>'

            # Plain text
            participants[status]['plain'] = participants[status]['plain'] + '{} [{}]\n'.format(record['Name'], record['DIN'])
            participants[status]['plain'] = participants[status]['plain'] + 'Custody: {}, Facility: {}\n'.format(record['Custody'], record['Facility'])
            if status == 'Changed':
                participants[status]['plain'] + 'CHANGES: {}\n'.format(record['Changes'])
    
    # Section header
    section_headers_dict = write_section_header()
    
    # HTML message
    html_message = '''
    <link rel="noopener" target="_blank" href="https://fonts.googleapis.com/css2?family='Roboto'&display=swap" rel="stylesheet">
    <div style="font-family: Roboto, Arial"; font-size:12px>
        <div align='center'>
            <img src="cid:{}" alt="finEQUITY_logo" width="450"/>
            <br>
        </div>
    <div>
        {}
        <br>
        {}
        {}
        <br>
        {}
        {}
    </div>
    <br>
    <body style="font-size:12px">
        <i>Brought to you by <a href="https://www.finequity.org/">finEQUITY.org</a></i>
    </body>
    <br>
    </div>
    '''.format(
        image_cid[1:-1],
        html_intro_text,
        section_headers_dict['Changed']['html'],
        participants['Changed']['html'],
        section_headers_dict['Unchanged']['html'],
        participants['Unchanged']['html'],
        )
    
    # Plain text message
    plain_text_message = '{}\n\n{}\n\n{}\n\n{}\n\n{}\n\n{}Brought to you by finEQUITY.org\n\https://www.finequity.org/\n\n'.format(
        'finEQUITY.org',
        plain_intro_text,
        section_headers_dict['Changed']['plain'],
        participants['Changed']['plain'],
        section_headers_dict['Unchanged']['plain'],
        participants['Unchanged']['plain'],
        )

    return html_message, plain_text_message

# Send message via GMail SMTP server
def send_email(compare_dict):

    print('Beginning send_email()')

    # Login
    account = os.environ.get('EMAIL_ACCOUNT')
    password = os.environ.get('GMAIL_SMTP_APP_PASSWORD')
    
    # Create message object
    msg = EmailMessage()
    msg['Subject'] = 'NYC Incarcerated Scraper Results'
    msg['From'] = account
    msg['To'] = account

    # Set message body, embed logo
    image_cid = make_msgid()
    html_message, plain_text_message = craft_message(compare_dict, image_cid)
    msg.set_content(plain_text_message)
    msg.add_alternative(html_message.format(image_cid=image_cid[1:-1]), subtype='html')
    with open('src/media/finEQUITY_logo.png', 'rb') as img:
        msg.get_payload()[1].add_related(img.read(), 'image', 'jpeg', cid=image_cid)
    
    # Send message via GMail SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        try:
            smtp_server.login(account, password)
        except Exception as e:
            print('Failed to log into Google SMTP Server, error:', e)
        smtp_server.send_message(msg)
    
    print('Completed send_email()')

