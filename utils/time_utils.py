import datetime
import time


def transfer_time(time_str):
    dt_obj = datetime.datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
    timeArray = dt_obj.astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')
    return  int(time.mktime(time.strptime(timeArray, "%Y-%m-%d %H:%M:%S")))