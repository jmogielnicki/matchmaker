from __future__ import print_function
import httplib2
import os
import random

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
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

OFFICE_LIST_RANGE_NAME = 'office_list!A2:C400'
OPT_OUT_RANGE_NAME = 'Form Responses 2!A2:C100'
OUTPUT_RANGE_NAME = 'matchmaker_output!A1:W400'
SPREADSHEET_ID = '1mb2_RuTwYXChc9wyebzVXJ75uh7mgqof220eZvFc9Iw'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_data_from_google_sheets(service, spreadsheetId, rangeName):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values


def make_matches(people, opt_outs):
    groups = []
    group_size = 2
    opt_outs_ldaps = [row[2] for row in opt_outs]
    people = [person for person in people if person[1] not in opt_outs_ldaps]
    random.shuffle(people)

    groups = [people[i:i + group_size] for i in range(0, len(people), group_size)]

    # If the last group is too small, add to last group
    if len(groups[-1]) < 2:
        leftovers = groups.pop()
        groups[-1] = groups[-1] + leftovers
    return groups


def write_groups_to_sheets(groups):

    credentials = get_credentials()
    service = discovery.build('sheets', 'v4', credentials=credentials)

    # The ID of the spreadsheet to update.
    spreadsheet_id = SPREADSHEET_ID

    # The A1 notation of the values to update.
    range_ = OUTPUT_RANGE_NAME  # TODO: Update placeholder value.

    # How the input data should be interpreted.
    value_input_option = 'RAW'  # TODO: Update placeholder value.

    value_range_body = {
        "range": OUTPUT_RANGE_NAME,
        "majorDimension": "ROWS",
        "values": groups
    }

    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption=value_input_option,
        body=value_range_body
    )
    response = request.execute()
    pprint(response)
    # service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()


def modify_data(matches):
    headers = [
        'person 1 name',
        'person 1 ldap',
        'person 1 team',
        'person 2 name',
        'person 2 ldap',
        'person 2 team',
        'person 3 name',
        'person 3 ldap',
        'person 3 team'
        ]
    # modified_matches = [match[0] + match[1] for match in matches]
    modified_matches = []
    for match in matches:
        match_list = []
        for item in match:
            match_list = match_list + item
        modified_matches.append(match_list)
    modified_matches.insert(0, headers)
    return modified_matches


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    office_people_list = get_data_from_google_sheets(service, SPREADSHEET_ID, OFFICE_LIST_RANGE_NAME)
    opt_out_list = get_data_from_google_sheets(service, SPREADSHEET_ID, OPT_OUT_RANGE_NAME)

    matches = make_matches(office_people_list, opt_out_list)
    # print(matches)
    matches = modify_data(matches)
    # print(matches)
    for match in matches:
        print(match)

    write_groups_to_sheets(matches)

if __name__ == '__main__':
    main()