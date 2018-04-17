from __future__ import print_function
import argparse
import random

import consts
import utils


def group_matches(data):
    matches = {}
    for person in data:
        person_match_id = person.get('match_id')
        if person_match_id not in matches:
            matches[person_match_id] = [person]
        else:
            matches[person_match_id].append(person)
    return matches


def get_match_key(person):
    return person.get('week_of')+'_'+person.get('match_id')

def append_blacklist(people, historical_matches):
    for person in people:
        blacklist = []
        # add the person's manager to their blacklist
        blacklist.append(person.get('manager_ldap'))
        match_keys = []
        # Loop through once to get match keys we need to identify historical matches
        for historical_person in historical_matches:
            if historical_person.get('ldap') == person.get('ldap'):
                match_keys.append(get_match_key(historical_person))
        # loop through again to find historical matches and add to blacklist
        for historical_person in historical_matches:
            if historical_person.get('ldap') != person.get('ldap') and get_match_key(historical_person) in match_keys:
                blacklist.append(historical_person.get('ldap'))
        person['blacklist'] = blacklist
    return people

def has_bad_match(people):
    grouped_matches = group_matches(people)
    for match_id, group in grouped_matches.iteritems():
        # print('___ match ' + str(match_id))
        total_blacklist = [blacklisted_person for person in group for blacklisted_person in person.get('blacklist')]
        # print('blacklist: ' + str(total_blacklist))
        for person in group:
            # print(person)
            if person.get('ldap') in total_blacklist:
                print('* found a bad match....starting over')
                return True
    return False


def make_matches(people, opt_outs):
    group_size = 2
    opt_outs_ldaps = [row[2] for row in opt_outs]
    people = [person for person in people if person.get('ldap') not in opt_outs_ldaps and person.get('out_of_office') != 'y']
    random.shuffle(people)

    match_id = 0
    for idx, person in enumerate(people):
        person['match_id'] = match_id
        # increment group number, unless we only have 1 person left in the list in which case include them in last group
        if idx % group_size == 1 and len(people) - idx > 2:
            match_id += 1

    # For now, we just look to see if anyone got matched with someone in their blacklist and if so we run the whole
    # thing again.  This is wildly inefficient and won't scale, so we need to figure out a better way
    if has_bad_match(people):
        make_matches(people, opt_outs)

    return people


def main(args):
    office_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OFFICE_LIST_RANGE_NAME)
    people = utils.convert_sheets_data_to_list_of_dicts(data=office_list)
    # import pdb; pdb.set_trace()
    opt_out_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OPT_OUT_RANGE_NAME)
    historical_matches = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.HISTORICAL_MATCHES_RANGE_NAME)
    historical_matches = utils.convert_sheets_data_to_list_of_dicts(historical_matches)

    people = append_blacklist(people, historical_matches)

    matches = make_matches(people, opt_out_list)
    matches = sorted(matches, key=lambda match: int(match.get('match_id')))
    fields_to_output = ['name', 'ldap', 'team', 'blacklist', 'match_id']
    matches = utils.convert_list_of_dicts_to_sheets_format(matches, fields_to_output)

    if args.write:
        utils.write_groups_to_sheets(matches, consts.SPREADSHEET_ID, consts.OUTPUT_RANGE_NAME)
    else:
        for match in matches:
            print(match)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--write', help='write the results to google sheet', action='store_true')
    args = parser.parse_args()
    main(args)
