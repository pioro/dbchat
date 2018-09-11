import json
import logging
import re
from datetime import datetime, timedelta
import pytz

database_list = {}


def loadconfig():
    global database_list
    connection_file = open('databases.json', 'r')
    database_list = json.load(connection_file)
    connection_file.close()


def get_list():
    global database_list
    return database_list

def convert_using_offset(timestamp, src, dst, printtz):
    """
    Convert timestamp from src timezone to dst timezone
    using a offset
    limited to/from UTC
    """
    logger = logging.getLogger()
    logger.debug("timestamp %s" % timestamp)
    logger.debug("timezones %s %s" % (src, dst))
    # fix for Heineken GMT+1 is not something we known
    # also depend on DST GMT+1 can be Europe/Amsterdam in Winter
    # or Europe/Dublin in summer

    m = re.match(r'(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)\.\d\d\dZ', timestamp)
    if m:
        ts = datetime.strptime(m.group(1) + ' ' + m.group(2),
                               '%Y-%m-%d %H:%M:%S')
    else:
        ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    if (src == 'UTC'):
        offset = re.match(r'GMT([+|-]\d\d)\:(\d\d)', dst)
        if offset:
            offsethours = offset.group(1)
            dst_ts = ts + timedelta(hours=int(offsethours))
    elif (dst == 'UTC'):
        offset = re.match(r'GMT([+|-]\d\d)\:(\d\d)', src)
        if offset:
            offsethours = offset.group(1)
            dst_ts = ts - timedelta(hours=int(offsethours))
    else:
        return None

    ret_ts = str(dst_ts.date()) + ' ' + \
        str(dst_ts.time())

    if printtz is not None:
        ret_ts = ret_ts + ' ' + 'GMT' + offsethours

    return ret_ts

def convert_timezone(timestamp, src, dst, printtz):
    """
    Convert timestamp from src timezone to dst timezone
    """
    logger = logging.getLogger()
    logger.debug("timestamp %s" % timestamp)
    logger.debug("timezones %s %s" % (src, dst))


    m = re.match(r'(\d\d\d\d-\d\d-\d\d)T(\d\d:\d\d:\d\d)\.\d\d\dZ', timestamp)
    if m:
        ts = datetime.strptime(m.group(1) + ' ' + m.group(2),
                               '%Y-%m-%d %H:%M:%S')
    else:
        ts = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    try:
        srctz = pytz.timezone(src)
        loc_ts = srctz.localize(ts)
        dsttz = pytz.timezone(dst)
        dst_ts = loc_ts.astimezone(dsttz)
        ret_ts = str(dst_ts.date()) + ' ' + \
            str(dst_ts.time())
        if printtz is not None:
            ret_ts = ret_ts + ' ' + str(dst_ts.tzname())

        return ret_ts
    except TypeError:
        return None


def convert_from_utc(timestamp, timezone, printtz=None):
    offset = re.match(r'GMT([+|-]\d\d)\:(\d\d)', timezone)
    if offset:
        return convert_using_offset(timestamp, 'UTC', timezone, printtz)
    else:
        return convert_timezone(timestamp, 'UTC', timezone, printtz)


def convert_to_utc(timestamp, timezone, printtz=None):
    offset = re.match(r'GMT([+|-]\d\d)\:(\d\d)', timezone)
    if offset:
        return convert_using_offset(timestamp, timezone, 'UTC', printtz)
    else:
        return convert_timezone(timestamp, timezone, 'UTC', printtz)
