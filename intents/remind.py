from intents.base import Remind, Help
import intents.utils as utils

import re
import logging

logger = logging.getLogger(__name__)

class IntentRemind(Remind):
    NAME = 'REMIND'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        pskey = self.bestCandidate()
        if not pskey:
            return Help.Response()
        query = self.request.Message()

        return self.Response(self.parse(query, pskey))

    def initSlots(self):
        slots = self.intent.slots.filter(type__startswith='user_rmd_').all()
        for slot in slots:
            f = slot.type[9:]
            if f == 'n':
                self.slot_n = slot
            elif f == 'v':
                self.slot_v = slot
            elif f == 'w':
                self.slot_w = slot
            elif f == 't':
                self.slot_t = slot

    def patterns(self):
        return { 
            'a': '[D:kw_plz][D:user_rmd_t][D:kw_plz][D:user_rmd_v][D:user_rmd_w][W:4-200]',
            'b': '[W:4-200][D:kw_sp][D:kw_plz][D:user_rmd_t][D:kw_plz][D:user_rmd_v][D:user_rmd_w][W:0-10]',
            'c': '[D:kw_plz][D:user_rmd_crt][W:0-10][D:user_rmd_n][W:0-10][D:kw_sp][W:4-200]',
           'ac': '[D:kw_plz][D:user_rmd_crt][W:0-10][D:user_rmd_n][W:4-200]',
            'd': '[D:kw_plz][D:user_rmd_v][D:user_rmd_w][W:4-200]',
            'e': '[W:4-200][D:kw_sp][D:kw_plz][D:user_rmd_v][D:user_rmd_w][W:0-10]',
            'f': '[D:user_rmd_n][D:kw_sp][W:4-200]',
            'g': '[D:kw_plz][D:kw_gen][D:user_rmd_w][D:kw_say][W:0-10][D:kw_sp][W:4-200]',
            'h': '[D:kw_plz][D:kw_for][D:user_rmd_w][D:user_rmd_crt][W:0-10][D:user_rmd_n][D:kw_sp][W:4-200]',
            'i': '[D:kw_plz][D:kw_for][D:user_rmd_w][W:0-10][D:user_rmd_n][D:kw_sp][W:4-200]',
            'j': '[D:kw_plz][D:kw_send][D:kw_one][W:0-10][D:user_rmd_n][D:kw_gei][D:user_rmd_w][D:kw_sp][W:4-200]',
            'k': '[D:kw_plz][D:kw_send][D:kw_gei][D:user_rmd_w][D:kw_one][W:0-10][D:user_rmd_n][D:kw_sp][W:4-200]',
            'l': '[D:kw_plz][D:user_rmd_crt][W:0-10][D:user_rmd_n][D:kw_gei][D:user_rmd_w][D:kw_sp][W:4-200]',
        }

    def bestCandidate(self):
        c = 0
        d = 0
        rmds = []
        candidate = None
        for v in self.intent.candidates.filter():
            c2 = float(v.intent_confidence)
            if c2 < c:
                continue
            d2 = len(re.findall(r'\[.+?\]', v.match_info))
            if c2 > c or not candidate:
                c = c2
                d = d2
                rmds = re.findall(r'\[D:user_rmd_[w|t]\]', v.match_info)
                candidate = v
                continue
            rmds2 = re.findall(r'\[D:user_rmd_[w|t]\]', v.match_info)
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

        if pskey in ['a']:
            return '{}提醒{}，{}'.format(
                self.slot_t.original_word, self.slot_w.original_word,
                utils.find_split_next(bq[self.slot_w.offset+self.slot_w.length:].decode('gbk'), 5),
            )
        if pskey in ['b']:
            return '{}提醒{}，{}'.format(
                self.slot_t.original_word, self.slot_w.original_word,
                utils.find_split_prev(bq[:self.slot_t.offset].decode('gbk'), 10),
            )
        if pskey in ['c', 'f', 'ac']:
            return '提醒我，{}'.format(
                utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 5),
            )
        if pskey in ['d']:
            return '提醒{}，{}'.format(
                self.slot_w.original_word,
                utils.find_split_next(bq[self.slot_w.offset+self.slot_w.length:].decode('gbk'), 5),
            )
        if pskey in ['e']:
            return '提醒{}，{}'.format(
                self.slot_w.original_word,
                utils.find_split_prev(bq[:self.slot_v.offset].decode('gbk'), 10),
            )
        if pskey in ['g', 'j', 'l']:
            return '提醒{}，{}'.format(
                self.slot_w.original_word,
                utils.find_split_next(bq[self.slot_w.offset+self.slot_w.length:].decode('gbk'), 10)
            )
        if pskey in ['h', 'i', 'k']:
            return '提醒{}，{}'.format(
                self.slot_w.original_word,
                utils.find_split_next(bq[self.slot_n.offset+self.slot_n.length:].decode('gbk'), 5)
            )

        return oquery
