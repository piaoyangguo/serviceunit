#! /usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys,os,django
__py_dir__ = os.path.split(os.path.realpath(__file__))[0]
__top_dir__ = os.path.dirname(__py_dir__)
sys.path.append(__top_dir__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serviceunit.settings")
django.setup() 

import time, json
from common.cntime import CNTime

Cases = [
    #'三分钟后',
    #'18号',
    #'18号前',
    #'18号后',
    #'18号内',
    #'18号左右',
    #'三天前',
    #'三天后',
    #'三天内',
    #'三天左右',
    #'三点前',
    #'三点后',
    #'三点内',
    #'三点左右',
    #'下午',
    #'三年前',
    #'本周',
    #'2月下半月',
    #'3天',
#    '前三天',
#    '后三天',
#    '最近',
#    '这几天',
#    '前1周',
#    '近3个小时',
    #'这阵子',
#    '前后3天',
#    '当前',
#    '0小时前',
    #'过去',
    '第一季度',
]

def main():
    global Cases
    print('---')
    for case in Cases:
        _ts = time.time()
        data = CNTime(case)
        #data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
        start, end = data.guess_time()
        print('{} => {}, ({}, {})'.format(case, data.desc_time(), start, end))
        _te = time.time()
        print('Assumed: {}ms'.format(round((_te - _ts) * 1000)))
        print('---')
    Cases = [
        ('8号', '13号'),
        ('三天前', '三天后'),
        ('前三天', '后三天'),
    ]
    for cfrom, cto in Cases:
        _ts = time.time()
        a = CNTime(cfrom)
        b = CNTime(cto)
        start, end = CNTime.Merge(a.guess_time(), b.guess_time())
        print('from {} to {}, ({}, {})'.format(
            a.desc_time(), b.desc_time(),
            start, end,
        ))
        _te = time.time()
        print('Assumed: {}ms'.format(round((_te - _ts) * 1000)))
        print('---')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as ki:
        pass
