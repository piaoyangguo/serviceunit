from intents.base import CreateTask, Help
import intents.utils as utils

import re
import logging

logger = logging.getLogger(__name__)

class IntentNewTask(CreateTask):
    NAME = 'NEW_TASK'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        query = self.request.Message()

        if self.request.Session:
            return self.GoWithSession()

        self.initSlots()
        pskey = self.bestCandidate()
        if not pskey:
            return Help.Response()

        cquery = self.parse(query, pskey)
        if type(cquery) == str:
            return self.Response(cquery)
        return self.ResponseNaked(query, self.request.UID(), cquery)

    def GoWithSession(self):
        query  = [self.request.Message()]
        _, payload = self.request.Session.GetPayload()
        if payload:
            if 't' in payload:
                query.insert(0, payload['t'])
            if 'w' in payload:
                query.insert(0, payload['w'])
        query = '，'.join(query)
        return self.Response(query)

    def initSlots(self):
        slots = self.intent.slots.filter(type__startswith='user_new_').all()
        for slot in slots:
            f = slot.type[9:]
            if f == 'n':
                self.slot_n = slot
            elif f == 'c':
                self.slot_c = slot
            elif f == 'w':
                self.slot_w = slot
            elif f == 't':
                self.slot_t = slot

    def patterns(self):
        return { 
            'a': '[D:kw_plz][D:user_new_t][D:kw_for][D:user_new_w][D:user_new_c][W:0-9][D:user_new_n][W:4-200]',
            'b': '[D:kw_plz][D:kw_for][D:user_new_w][W:0-10][D:user_new_t][D:user_new_c][D:user_new_n][W:4-200]',
            'c': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_t][W:4-200][D:kw_de][D:user_new_n]',
            'd': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][W:0-10][D:user_new_n][D:kw_sp][W:4-200]',
            'f': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][W:4-200][D:kw_de][D:user_new_n]',
            'g': '[D:kw_for][D:user_new_w][D:user_new_c][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][D:user_new_t]',
            'i': '[D:kw_plz][D:user_new_c][W:0-10][D:user_new_n][D:kw_sp][W:4-200]',

            'l': '[D:user_new_c][D:user_new_t][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][W:0-4][D:user_new_w][W:0-4]',
            'e': '[D:kw_plz][D:user_new_c][D:user_new_t][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][W:4-200]',

            'j': '[D:kw_plz][D:user_new_c][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][W:0-4][D:user_new_t][W:0-4]',
            'k': '[D:kw_plz][D:user_new_c][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][W:0-4][D:user_new_w][W:0-4]',
            'h': '[D:kw_plz][D:user_new_c][W:4-200][D:kw_de][D:user_new_n][D:kw_sp][W:4-200]',
            'm': '[D:kw_plz][D:user_new_c][W:4-200][D:kw_de][D:user_new_n]',

          'x01': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_t][D:kw_de][D:user_new_n]',
          'x02': '[D:kw_plz][D:user_new_c][D:user_new_t][D:kw_de][D:user_new_n][W:0-4][D:user_new_w][W:0-3]',
          'x03': '[D:kw_plz][D:user_new_c][D:user_new_t][D:kw_de][D:user_new_n][W:0-4]',
          'x04': '[D:kw_plz][D:user_new_t][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_n][W:0-4]',
          'x05': '[D:kw_plz][D:kw_for][D:user_new_w][W:0-10][D:user_new_t][D:user_new_c][D:user_new_n][W:0-4]',
          'x06': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_t][D:kw_done][D:kw_de][D:user_new_n]',
          'x07': '[D:kw_plz][D:user_new_c][D:user_new_t][D:kw_done][D:kw_de][D:user_new_n][W:0-4][D:user_new_w][W:0-3]',
          'x08': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_n][W:0-4][D:user_new_t][W:0-3]',
          'x09': '[D:kw_plz][D:user_new_c][W:0-4][D:user_new_n][W:0-4][D:user_new_t][W:0-4][D:user_new_w][W:0-3]',
          'x10': '[D:kw_plz][D:user_new_c][W:0-4][D:user_new_n][W:0-4][D:user_new_w][W:0-4][D:user_new_t][W:0-3]',
          'x11': '[D:kw_plz][D:kw_for][D:user_new_w][D:user_new_c][D:user_new_n][W:0-4]',
          'x12': '[D:kw_plz][D:user_new_c][D:user_new_n][W:0-4][D:user_new_w][W:0-3]',
          'x13': '[D:kw_plz][D:user_new_c][W:0-10][D:kw_is][D:user_new_w][D:kw_de][D:user_new_n][W:0-4]',
          'x14': '[D:kw_plz][D:user_new_t][D:user_new_c][D:user_new_n][W:0-4]',
          'x15': '[D:kw_plz][D:user_new_c][D:user_new_t][D:kw_done][D:kw_de][D:user_new_n][W:0-4]',
          'x16': '[D:kw_plz][D:user_new_c][W:0-4][D:user_new_n][W:0-4][D:user_new_t][W:0-3]',
          'x17': '[D:kw_plz][D:user_new_c][W:0-10][D:kw_is][D:user_new_t][D:kw_de][D:user_new_n][W:0-4]',
          'x18': '[D:kw_plz][D:user_new_c][W:0-4][D:user_new_n][W:0-3]',
          'x19': '[D:kw_plz][D:user_new_c][D:kw_for][D:user_new_w][D:kw_de][D:user_new_n][W:0-4]',
        }

    def bestCandidate(self):
        c = 0
        d = 0
        rmds = []
        candidate = None
        for v in self.intent.candidates.filter():
            if '[D:user_task]' in v.match_info:
                continue
            c2 = float(v.intent_confidence)
            if c2 < c:
                continue
            d2 = len(re.findall(r'\[.+?\]', v.match_info))
            if c2 > c or not candidate:
                c = c2
                d = d2
                rmds = re.findall(r'\[D:user_new_[w|t]\]', v.match_info)
                candidate = v
                continue
            rmds2 = re.findall(r'\[D:user_new_[w|t]\]', v.match_info)
            if len(rmds2) > len(rmds) or \
               (len(rmds2) == len(rmds) and d2 > d) or \
               (len(rmds2) == len(rmds) and d2 == d and len(v.match_info) > len(candidate.match_info)):
                c = c2
                d = d2
                rmds = rmds2
                candidate = v

        self.kws = {}
        key = ''
        if candidate and candidate.match_info:
            tgt = candidate.match_info
            kws = re.findall(r'kw_(\w+):([^\|]+)', tgt)
            for k, v in kws:
                v = (v, len(v.encode('gbk')))
                if k in self.kws:
                    if type(self.kws[k]) == tuple:
                        self.kws[k] = [self.kws[k]]
                    self.kws[k].append(v)
                else:
                    self.kws[k] = v
            value = ''
            for k, v in self.patterns().items():
                if not tgt.startswith(v):
                    continue
                if len(v) < len(value):
                    continue
                key = k 
                value = v 
            kw_plz = '[D:kw_plz]'
            if not tgt.startswith(kw_plz):
                tgt = kw_plz + tgt
                for k, v in self.patterns().items():
                    if not tgt.startswith(v):
                        continue
                    if len(v) < len(value):
                        continue
                    key = k 
                    value = v 
        if key:
            logger.debug('{} matched {} use {}'.format(self.NAME, key, tgt))
        return key

    def parse(self, oquery, pskey):
        bq = oquery.encode('gbk')

        if pskey in ['a', 'b']:
            return '{}，{}，{}'.format(
                self.slot_w.original_word, self.slot_t.original_word,
                utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 2),
            )
        if pskey in ['c']:
            return '{}，{}'.format(
                self.slot_w.original_word,
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
        if pskey in ['d']:
            return '{}，{}'.format(
                self.slot_w.original_word,
                utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 2),
            )
        if pskey in ['e', 'l']:
            query = '{}'.format(
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
            if pskey == 'e':
                if query[-2:] == '开始':
                    query = query[:-2]
                elif query[-1] == '做':
                    query = query[:-1]
                return '{}，{}'.format(
                    query,
                    utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 2),
                )
            if pskey == 'l':
                return '{}，{}'.format(self.slot_w.original_word, query)
        if pskey in ['f']:
            return '{}，{}'.format(
                self.slot_w.original_word,
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
        if pskey in ['g']:
            return '{}，{}，{}'.format(
                self.slot_w.original_word, self.slot_t.original_word,
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
        if pskey in ['h', 'j', 'k']:
            query = '{}'.format(
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
            if pskey == 'h':
                if query[-2:] == '开始':
                    query = query[:-2]
                elif query[-1] == '做':
                    query = query[:-1]
                return '{}，{}'.format(
                    query,
                    utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 2),
                )
            if pskey == 'j':
                return '{}，{}'.format(self.slot_t.original_word, query)
            if pskey == 'k':
                return '{}，{}'.format(self.slot_w.original_word, query)
        if pskey in ['i']:
            return '{}'.format(
                utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 2),
            )
        if pskey in ['m']:
            return '{}'.format(
                utils.find_de_prev(bq[self.slot_c.offset+self.slot_c.length:self.slot_n.offset].decode('gbk'), 2),
            )
        if pskey[0] == 'x':
            payload = {}
            if hasattr(self, 'slot_t'):
                payload['t'] = self.slot_t.original_word
            if hasattr(self, 'slot_w'):
                payload['w'] = self.slot_w.original_word
            return payload

        return oquery
