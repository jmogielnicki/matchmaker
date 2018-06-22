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
    people_dict = dict([(x.get('ldap'), x) for x in people])
    for person in people:
        person['blacklist'] = []
    for person in people:
        blacklist = person.get('blacklist')
        # add the person's manager to their blacklist
        manager_ldap = person.get('manager_ldap')
        blacklist.append(manager_ldap)
        if manager_ldap != 'none': 
            # print( person)
            # print(manager_ldap)
            # print(people_dict.get(manager_ldap))
            people_dict.get(manager_ldap).get('blacklist').append(person.get('ldap'))
        match_keys = []
        team = person['team']
        if team != 'Other':
            for office_mate in people_dict.keys():
                if person['ldap'] == office_mate:
                    continue
                if people_dict.get(office_mate)['team'] == team and office_mate not in blacklist:
                    blacklist.append(office_mate)
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

def get_match_for_person(person, people_dict):
    all_people = people_dict.keys()
    # print("%s" % person)
    filtered_people =  list(set(all_people)-set(people_dict.get(person).get('blacklist')))
    if filtered_people:
        return [person, filtered_people[random.randint(0,len(filtered_people)-1)]]
    else:
        return None

def add_last_person(person, people):
    filtered_people = people[:]
    filtered_people.remove(person)
    match_id_dict = dict([(x.get('match_id'), [x]) for x in filtered_people])
    for p in filtered_people:
        if p not in match_id_dict.get(p.get('match_id')):
            match_id_dict[p.get('match_id')].append(p)
    # import pdb; pdb.set_trace();
    blacklist = person.get('blacklist')
    for matchid, people in match_id_dict.iteritems():
        if people[0].get('ldap') not in blacklist and people[1].get('ldap') not in blacklist:
            return matchid
    return None

def make_matches(people, opt_outs):
    print("make matches called!")
    group_size = 2
    opt_outs_ldaps = [row[2] for row in opt_outs]
    filtered_people = [person for person in people if person.get('ldap') not in opt_outs_ldaps and person.get('out_of_office') != 'y']
    # (to test for odd number) filtered_people = filtered_people[1:]
    people_dict = dict([(x.get('ldap'), x) for x in filtered_people])
    random.shuffle(filtered_people)
    remaining_people = [x.get('ldap') for x in filtered_people]
    match_idx = 0
    for person in filtered_people:
        if person.get('ldap') not in remaining_people:
            continue
        remaining_people.remove(person.get('ldap'))
        options = list(set(remaining_people) - set(person.get('blacklist')))
        # print(person.get('ldap') + ': ' + str(options)) 
        if not options and not remaining_people:
            result = add_last_person(person, filtered_people)
            if result:
                person['match_id'] = result
            else:
                make_matches(people, opt_outs)
        elif not options:
            make_matches(people, opt_outs)
        else:
            match = people_dict.get(random.choice(options))
            person['match_id'] = match_idx
            match['match_id'] = match_idx
            remaining_people.remove(match.get('ldap'))
            match_idx += 1
    return filtered_people




def main(args):
    office_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OFFICE_LIST_RANGE_NAME)
    people = utils.convert_sheets_data_to_list_of_dicts(data=office_list)
    opt_out_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.OPT_OUT_RANGE_NAME)
    historical_matches = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.HISTORICAL_MATCHES_RANGE_NAME)
    historical_matches = utils.convert_sheets_data_to_list_of_dicts(historical_matches)

    people = append_blacklist(people, historical_matches) 
    # print(people)
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
