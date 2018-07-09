import consts
import utils
import itertools
from operator import itemgetter
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError

def convert_data(data):
    historical_match_list = utils.convert_sheets_data_to_list_of_dicts(data=data)
    pivoted_matches = utils.pivot_list_of_dicts_to_nested_dict(historical_match_list, 'week_of')
    for date_key in pivoted_matches:
        pivoted_matches[date_key] = utils.pivot_list_of_dicts_to_nested_dict(pivoted_matches[date_key], 'match_id')
    return pivoted_matches

def get_match_rate(data):
    # count = 0
    # end_time = datetime.utcnow()
    # start_time = end_time - timedelta(days=16)
    stats = []
    for week_id, week_data in data.iteritems():
        num_groups = len(week_data)
        count = 0
        # import pdb;pdb.set_trace()
        end_time = datetime.strptime(str(week_id), '%m/%d/%Y')
        start_time = end_time - timedelta(days=18)
        print week_id
        # print week_id
        # if week_id == '4/2/2018':
        for match_id, match_data in week_data.iteritems():
            # print '_____________________'
            # print match_data
            group_did_meet = False
            source = match_data[0]
            source_ldap = source.get('ldap')
            target = match_data[1]
            try:
                source_calendar_data = utils.get_calendar_events(source_ldap, start_time, end_time)
                source_events = source_calendar_data.get('items')
                for event in source_events:
                    attendees = event.get('attendees')
                    if attendees and len(attendees) == 2:
                        target_email = '{0}@pinterest.com'.format(target.get('ldap'))
                        if target_email in [attendee.get('email') for attendee in attendees]:
                            # print '__ group met!'
                            # print attendees
                            group_did_meet = True
                        # for attendee in attendees:
                        #     if attendee.get('email') == '{0}@pinterest.com'.format(target.get('ldap')):
                if group_did_meet:
                    count += 1
                else:
                    pass
                    # print '__ group did not meet'
            except HttpError:
                # print 'Error: skipping'
                pass
        print 'week of ' + week_id
        print 'groups that met: ' + str(count)
        print 'total groups: ' + str(int(num_groups))

    return count
                # print match_id
                # for index, person in match_data.iteritems():
                #     if person.get('ldap') == 'jmogielnicki':
                #         person['calendar_data'] = utils.get_calendar_events(person.get('ldap'), start_time, end_time)
    # import pdb; pdb.set_trace()

def main():
    historical_match_list = utils.get_data_from_google_sheets(consts.SPREADSHEET_ID, consts.HISTORICAL_MATCHES_RANGE_NAME)
    pivoted_match_list = convert_data(historical_match_list)
    match_rate = get_match_rate(pivoted_match_list)
    print(match_rate)
    # calendar_info = utils.get_calendar_events()
    # events = calendar_info.get('items')
    # for event in events:
    #     attendees = event.get('attendees')
    #     if attendees and len(attendees) == 2:
    #         for attendee in attendees:
    #             print attendee.get('email')
    # import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()