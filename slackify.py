import consts
import utils
import itertools
from operator import itemgetter

def print_slackified_matches(data):
    match_string = ''
    matches = utils.convert_sheets_data_to_list_of_dicts(data=data)
    sorted_matches = sorted(matches, key=itemgetter('match_id'))
    for match_id, match in itertools.groupby(sorted_matches, key=itemgetter('match_id')):
        for person in match:
            match_string += '@'
            match_string += person.get('ldap')
            match_string += ' '
        match_string += '\n'
    print match_string

def main():
    match_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OUTPUT_RANGE_NAME)
    print_slackified_matches(match_list)

if __name__ == '__main__':
    main()
