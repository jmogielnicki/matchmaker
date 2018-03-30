from __future__ import print_function
import random

from consts import OFFICE_LIST_RANGE_NAME, OPT_OUT_RANGE_NAME, OUTPUT_RANGE_NAME, SPREADSHEET_ID
from utils import get_data_from_google_sheets, write_groups_to_sheets

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

# OFFICE_LIST_RANGE_NAME = 'office_list!A2:C400'
# OPT_OUT_RANGE_NAME = 'Form Responses 2!A2:C100'
# OUTPUT_RANGE_NAME = 'matchmaker_output!A1:W400'
# SPREADSHEET_ID = '1mb2_RuTwYXChc9wyebzVXJ75uh7mgqof220eZvFc9Iw'


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
    office_people_list = get_data_from_google_sheets(SPREADSHEET_ID, OFFICE_LIST_RANGE_NAME)
    opt_out_list = get_data_from_google_sheets(SPREADSHEET_ID, OPT_OUT_RANGE_NAME)

    matches = make_matches(office_people_list, opt_out_list)
    # print(matches)
    matches = modify_data(matches)
    # print(matches)
    for match in matches:
        print(match)

    write_groups_to_sheets(matches, SPREADSHEET_ID, OUTPUT_RANGE_NAME)


if __name__ == '__main__':
    main()