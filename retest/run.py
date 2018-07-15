#! /usr/bin/env python3
import os, sys
os.environ.setdefault('UNIT_ENV', 'test')
AGENT  = os.environ.get('UNIT_TEST_AGENT', 'WXOA')
USERID = os.environ.get('UNIT_TEST_USERID', 'oXsrqst9usgnJ9QIzwfk78rO6SNw')
REFILE = os.environ.get('UNIT_TEST_REFILE', 'retest.log')
NUMCASE = int(os.environ.get('UNIT_TEST_NUMCASE', 100))

import reg
import time
from polymer import Polymer

from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/cases/*.py")
for f in modules:
    if isfile(f) and not f.endswith('__init__.py'):
        __import__('cases.' + basename(f)[:-3])

import api

def Test(f, name, num):
    rules = reg.Rules.get(name)
    handlers = reg.Handlers.get(name, [])

    ts0 = time.strftime('%H:%M:%S')

    numpass = 0
    numfail = {
        '1': 0,
    }
    ki = None
    try:
        for case in Polymer.ModelsChooser(rules, num).Gen():
            sentence = ''.join([v[1] for v in case])
            ts = time.time()
            intent = api.Do(AGENT, USERID, sentence)
            if intent.NAME == name:
                # TODO: match handlers
                #resp = intent.Go()
                msg = '{}, {}ms, +pass, {} {}'.format(
                    time.strftime('%H:%M:%S'),
                    int((time.time() - ts) * 1000),
                    name, sentence,
                )
                numpass += 1
            else:
                msg = '{}, {}ms, -fail, 1(intent dismatch), {} => {} {}'.format(
                    time.strftime('%H:%M:%S'),
                    int((time.time() - ts) * 1000),
                    name, intent.NAME, sentence,
                )
                numfail['1'] += 1
            f.write(msg+'\n')
            print(msg)
    except KeyboardInterrupt as e:
        ki = e
    tfail = 0
    for k in numfail:
        tfail += numfail[k]
    total = numpass+tfail
    msg = 'Passed {}, Total {}, {}, {}-{}'.format(
        str(round(numpass/total*100, 1))+'%' if total else 'N/A',
        total, name,
        ts0, time.strftime('%H:%M:%S'),
    )
    msg = '{}\n{}\n{}'.format(
        '---', msg, '---',
    )
    f.write(msg+'\n')
    print(msg)
    if ki:
        raise ki
    return numpass, tfail, numfail


def main():
    f = open(REFILE, 'w')
    if len(sys.argv) > 2:
        Test(f, sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) > 1:
        Test(f, sys.argv[1], NUMCASE)
    else:
        for name in reg.Rules:
            Test(f, name, NUMCASE)


if __name__ == '__main__':
    try:
        open('info.log', 'w').close()
        main()
    except KeyboardInterrupt as ki:
        pass
