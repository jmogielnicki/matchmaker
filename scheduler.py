import consts
import utils
from datetime import datetime, timedelta
from dateutil.parser import parse
import pytz

def find_common_free_time():
  work_hours = [11,13,14,15,16]
  for i in work_hours:
    for half_hour_interval in [0, 30]:
      print(i, half_hour_interval)




def main():
  tz = pytz.timezone(consts.TIMEZONE)
  START_DATE = tz.localize(datetime.now() + timedelta(days=1))
  END_DATE = tz.localize((datetime.now() + timedelta(days=10)))

  cal_dict = utils.get_calendar_events(START_DATE, END_DATE)
  for cal_name in cal_dict:
      print(cal_name)
      for busy_block in cal_dict[cal_name].get('busy'):
        busy_block['start_datetime'] = parse(busy_block.get('start'))
        busy_block['end_datetime'] = parse(busy_block.get('end'))
  # j_times = cal_dict['jmogielnicki@pinterest.com'].get('busy')
  # n_times = cal_dict['ncheng@pinterest.com'].get('busy')
  find_common_free_time(cal_dict)


if __name__ == '__main__':
    main()
