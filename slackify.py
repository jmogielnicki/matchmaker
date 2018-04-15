import consts
import utils

def print_slackified_matches(data):
    matches = utils.dictify_match_data(data=data)
    match_string = ''
    match_ids = sorted([int(key) for key in matches.keys()])
    for match_id in match_ids:
        match_string += 'match {}: '.format(match_id)
        list_of_matches = matches[str(match_id)]
        for person in list_of_matches:
            match_string += '@'
            match_string += person.get('ldap')
            match_string += ' '
        match_string += '\n'
    print(match_string)

def main():
    match_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OUTPUT_RANGE_NAME)
    print_slackified_matches(match_list)

if __name__ == '__main__':
    main()
