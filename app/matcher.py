import calendar
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List

re_date = re.compile('\d{4}-\d\d-\d\d')
re_datetime = re.compile('\d{4}-\d\d-\d\d\|\d\d:\d\d:\d\d')
re_interval = re.compile('(\d{4}-\d\d-\d\d)~(\d{4}-\d\d-\d\d)')


def try_format_date(date):
    try:
        if re_datetime.match(date):
            return datetime.strptime(date, '%Y-%m-%d|%H:%M:%S')
        elif re_date.match(date):
            return datetime.strptime(date, '%Y-%m-%d')
    except ValueError as e:
        logging.error(e)
    return None


def to_seconds(date, offset=0):
    if isinstance(date, str):
        date = try_format_date(date)
    if offset:
        date = date + timedelta(days=offset)
    return int(time.mktime(date.timetuple()) * 1000)


def to_date(seconds: int):
    date = datetime.fromtimestamp(seconds / 1000)
    return date.strftime('%Y-%m-%d %H:%M')


def exact_a_day(date: datetime):
    return to_seconds(date.date()), to_seconds(date + timedelta(days=1)) - 1000


def exact_a_month(date: datetime):
    weekday, days = calendar.monthrange(date.year, date.month)
    start = datetime(date.year, date.month, 1)
    end = datetime(date.year, date.month, days)
    return to_seconds(start), to_seconds(end + timedelta(days=1)) - 1000


def replace_date_zero(date: str, month='01', day='01'):
    if date[5:7] == '00':
        date = date[:5] + month + date[7:]
    if date[-2:] == '00':
        date = date[:-2] + day
    return date


def parse_time(query, original_word, normalized_word):
    # 2018-05-17~2018-05-23
    # 2018-05-17|09:00:00
    if not normalized_word:
        start, end = extract_time(query, original_word)
    elif '~' in normalized_word:
        a, b = normalized_word.split('~')
        a = replace_date_zero(a, '01', '01')
        b = replace_date_zero(b, '12', '00')
        if b[-2:] == '00':
            weekday, days = calendar.monthrange(int(b[:4]), int(b[5:7]))
            b = b[:-2] + str(days)
        start, end = to_seconds(a), to_seconds(b, 1) - 1000
    else:
        date = try_format_date(normalized_word)
        if date:
            start, end = exact_a_day(date)
        else:
            start, end = extract_time(query, normalized_word)
            if not start:
                start, end = extract_time(query, original_word)
    return start, end


def extract_time(query, time_word):
    now = datetime.now()

    time_slots = ['前天', '昨天', '今天', '明天', '后天']
    time_values = [-2, -1, 1, 2, 3]
    for slot, val in zip(time_slots, time_values):
        if slot in time_word:
            if val < 0:
                return to_seconds(now.date(), val), to_seconds(now.date(), val + 1) - 1000
            else:
                return to_seconds(now.date(), val - 1), to_seconds(now.date(), val) - 1000

    if '本月' in time_word:
        return exact_a_month(now)

    time_slots = ['1天', '2天', '3天', '4天', '5天', '一天', '两天', '三天', '四天', '五天', '一周', '下周', '几天', '近期']
    time_values = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 7, 7, 7, 7, 30]
    interval = 7
    for slot, val in zip(time_slots, time_values):
        if slot in time_word:
            interval = val
            break
    if is_future_time(query, time_word):
        return to_seconds(now.date()), to_seconds(now.date(), interval) - 1000
    if is_earlier_time(query, time_word):
        return to_seconds(now.date(), -interval), to_seconds(now.date(), 1) - 1000
    if is_within_time(query, time_word):
        return to_seconds(now.date(), -interval/2), to_seconds(now.date(), interval/2) - 1000
    return 0, 0


def is_future_time(query, time_word):
    word_list = ['未来', '将来']
    return match_word(time_word, word_list) or match_sentence(time_word, word_list, query)


def is_earlier_time(query, time_word):
    word_list = ['最近', '近']
    return match_word(time_word, word_list) or match_sentence(time_word, word_list, query)


def is_within_time(query, time_word):
    word_list = ['这',]
    if match_word(time_word, word_list):
        return True

    if match_sentence(time_word, word_list, query):
        return True

    word_list = ['内',]
    return match_word(time_word, word_list) or match_sentence(time_word, word_list, query, search_after=True)


def match_sentence(time_word, word_list, query, search_before=True, search_after=False):
    idx = query.find(time_word)
    if idx == -1:
        return False

    for standard in word_list:
        if search_before and standard + time_word in query:
            return True
        if search_after and time_word + standard in query:
            return True
    return False


def match_file_keyword(word):
    word_list = ['文档', '文章', '文件']
    return match_word(word, word_list)


def match_word(word, word_list):
    for standard in word_list:
        if standard in word:
            return True
    return False


def extract_watch(content):
    keys_slots = ['关注', ]
    for slot in keys_slots:
        if slot in content:
            return slot
    return ''
