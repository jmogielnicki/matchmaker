from consts import OUTPUT_RANGE_NAME, SPREADSHEET_ID
from utils import get_data_from_google_sheets, write_groups_to_sheets, dictify_data

def print_slackified_matches(data):
    matches = dictify_data(data)
    count = 1
    match_string = ''
    for key, list_of_matches in matches.iteritems():
        match_string += 'match {}: '.format(count)
        for person in list_of_matches:
            match_string += '@'
            match_string += person.get('ldap')
            match_string += ' '
        match_string += '\n'
        count += 1
    print(match_string)

def main():
    match_list = get_data_from_google_sheets(SPREADSHEET_ID, OUTPUT_RANGE_NAME)
    print_slackified_matches(match_list)

if __name__ == '__main__':
    main()
