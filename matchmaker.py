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
    group_size = 2
    opt_outs_ldaps = [row[2] for row in opt_outs]
    people = [person for person in people if person[1] not in opt_outs_ldaps]
    random.shuffle(people)

    match_number = 0
    for idx, person in enumerate(people):
        person.append(match_number)
        # increment group number
        # Do not increment if we only have 1 person left in the list - instead include them in last group
        if idx % group_size == 1 and len(people) - idx > 2:
            match_number += 1

    return people


def apply_header(matches):
    headers = [
        'name',
        'ldap',
        'team',
        'match_id',
        ]
    matches.insert(0, headers)
    return matches



def main():
    office_people_list = get_data_from_google_sheets(SPREADSHEET_ID, OFFICE_LIST_RANGE_NAME)
    opt_out_list = get_data_from_google_sheets(SPREADSHEET_ID, OPT_OUT_RANGE_NAME)

    matches = make_matches(office_people_list, opt_out_list)
    matches = apply_header(matches)

    write_groups_to_sheets(matches, SPREADSHEET_ID, OUTPUT_RANGE_NAME)


if __name__ == '__main__':
    main()