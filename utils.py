from __future__ import print_function
import httplib2
import os
import datetime
import pytz
import consts

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from pprint import pprint

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES_SHEETS = 'https://www.googleapis.com/auth/spreadsheets'
SCOPES_CALENDAR = 'https://www.googleapis.com/auth/calendar'
BASE_CREDENTIALS_PATH_SHEETS = 'sheets.googleapis.com'
BASE_CREDENTIALS_PATH_CALENDAR = 'calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'



def get_credentials(type):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    base_credentials_string = BASE_CREDENTIALS_PATH_CALENDAR if type == 'calendar' else BASE_CREDENTIALS_PATH_SHEETS
    scope = SCOPES_CALENDAR if type == 'calendar' else SCOPES_SHEETS
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   '{0}-python-quickstart.json'.format(base_credentials_string))

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_http(type):
    credentials = get_credentials(type)
    http = credentials.authorize(httplib2.Http())
    return http

def get_sheets_service():
    http = get_http('sheets')
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    return service


def get_calendar_service():
    http = get_http('calendar')
    service = discovery.build('calendar', 'v3', http=http)
    return service


def get_calendar_events(start_date, end_date, ids):
    # This event should be returned by freebusy
    service = get_calendar_service()
    items = []
    for id in ids:
        items.append({"id": id})
    body = {
      "timeMin": start_date.isoformat(),
      "timeMax": end_date.isoformat(),
      "timeZone": consts.TIMEZONE,
      "items": items,
    }

    eventsResult = service.freebusy().query(body=body).execute()
    cal_dict = eventsResult[u'calendars']
    return cal_dict

    # This returns all details of meetings on calendars.
    # service = get_calendar_service()
    # now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    # eventsResult = service.events().list(
    #     calendarId='jmogielnicki@pinterest.com', timeMin=now, maxResults=10, singleEvents=True,
    #     orderBy='startTime').execute()
    # return eventsResult

def create_calendar_event():
    service = get_calendar_service()
    event = {
        'summary': 'This is a test',
        'location': '',
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2018-04-07T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2018-04-07T11:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [
            {'email': 'jmogielnicki@gmail.com'},
            {'email': 'misspetry@gmail.com'},
        ],
        'reminders': {
            'useDefault': True,
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    # print 'Event created: %s' % (event.get('htmlLink'))


def get_data_from_google_sheets(spreadsheetId, rangeName):
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def write_groups_to_sheets(groups, spreadsheet_id, range):
    service = get_sheets_service()

    # How the input data should be interpreted.
    value_input_option = 'RAW'

    value_range_body = {
        "range": range,
        "majorDimension": "ROWS",
        "values": groups
    }

    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption=value_input_option,
        body=value_range_body
    )
    response = request.execute()
    pprint(response)


def dictify_data(data):
    headers = data[:1]
    headers = headers[0]
    people = data[1:]
    matches = {}
    for person in people:
        person_as_dict = dict(zip(headers, person))
        match_id = person_as_dict.get('match_id')
        if not matches.get(match_id):
            matches[match_id] = [person_as_dict]
        else:
            matches[match_id].append(person_as_dict)
    return matches
