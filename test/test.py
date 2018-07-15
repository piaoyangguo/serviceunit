#! /usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys,os,django
__py_dir__ = os.path.split(os.path.realpath(__file__))[0]
__top_dir__ = os.path.dirname(__py_dir__)
sys.path.append(__top_dir__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serviceunit.settings")
django.setup() 

import time, json

Cases = [
    'Hello world',
]

def main():
    global Cases
    print('---')
    for case in Cases:
        _ts = time.time()
        data = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
        start, end = data.guess_time()
        print(data)
        _te = time.time()
        print('Assumed: {}ms'.format(round((_te - _ts) * 1000)))
        print('---')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as ki:
        pass
