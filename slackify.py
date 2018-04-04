import consts
import utils

def print_slackified_matches(data):
    matches = utils.dictify_data(data)
    print matches
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
    match_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OUTPUT_RANGE_NAME)
    print_slackified_matches(match_list)

if __name__ == '__main__':
    main()
