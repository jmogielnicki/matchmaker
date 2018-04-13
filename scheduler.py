import consts
import utils
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import tzlocal
from pytz import timezone

RANGE_IN_DAYS = 6

# start and end time for calendar freebusy
START_DATETIME_FREEBUSY = datetime.now(tzlocal())
END_DATETIME_FREEBUSY = datetime.now(tzlocal()) + timedelta(days=RANGE_IN_DAYS)
# start checking calendars 2 days after the day the script is run
# buffer time so meeting is not immediately after announcement
START_DATE_CALENDAR_MATCHING = START_DATETIME_FREEBUSY.date() + timedelta(days=2)
END_DATE_CALENDAR_MATCHING = END_DATETIME_FREEBUSY.date() + timedelta(days=-1)


def daterange_weekdays(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        date = start_date + timedelta(n)
        if date.weekday() < 5:
          print date.weekday()
          yield date
        
def dates_and_times_to_check():
  work_hours = [13,14,15,16]
  for date in daterange_weekdays(START_DATE_CALENDAR_MATCHING, END_DATE_CALENDAR_MATCHING):
    for hour in work_hours:
      for minute in [0, 30]:
        date_and_time = datetime.combine(date, datetime.min.time())
        date_and_time = date_and_time.replace(hour=hour, minute=minute)
        pst = timezone(consts.TIMEZONE)
        date_and_time = pst.localize(date_and_time)
        print date_and_time
        yield date_and_time


def print_calendar(calendar_info):
  for match, calendar in calendar_info.iteritems():
    print '__________'
    print match
    for busy_block in calendar.get('busy'):
      print('from {0} to {1}').format(busy_block.get('start_datetime'), busy_block.get('end_datetime'))



def get_calendar_info():
  ids = ['jmogielnicki@pinterest.com', 'ncheng@pinterest.com']
  cal_dict = utils.get_calendar_events(START_DATETIME_FREEBUSY, END_DATETIME_FREEBUSY, ids)
  for cal_name in cal_dict:
      for busy_block in cal_dict[cal_name].get('busy'):
        busy_block['start_datetime'] = parse(busy_block.get('start'))
        busy_block['end_datetime'] = parse(busy_block.get('end'))
  j_times = cal_dict['jmogielnicki@pinterest.com'].get('busy')
  # for each in j_times:
    # print each['start_datetime'], each['end_datetime']
  print_calendar(cal_dict)

  return cal_dict
  # n_times = cal_dict['ncheng@pinterest.com'].get('busy')


def overlaps(block_start, block_end, time_to_check):
  # Hacky way to check both the start of the half hour block and a time partway through to ensure the block is open
  return block_start <= time_to_check < block_end or block_start <= time_to_check + timedelta(minutes=16) < block_end 

def find_common_free_time(calendar_info):
  # import pdb; pdb.set_trace()
  available_times = []

  for date_and_time in dates_and_times_to_check():
    is_available_for_everyone = True
    for match, calendar in calendar_info.iteritems():
      # print '__________'
      # print match
      for busy_block in calendar.get('busy'):
        # print('from {0} to {1}').format(busy_block.get('start_datetime'), busy_block.get('end_datetime'))
        if overlaps(busy_block.get('start_datetime'), busy_block.get('end_datetime'), date_and_time):
          is_available_for_everyone = False
    if is_available_for_everyone:
      available_times.append(date_and_time)
  return available_times



def main():
  calendar_info = get_calendar_info()
  common_free_time_list = find_common_free_time(calendar_info)

  print '_____________________ and the winners are...'
  for each in common_free_time_list:
    print each
  utils.create_calendar_event()

if __name__ == '__main__':
    main()
