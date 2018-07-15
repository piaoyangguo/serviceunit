from intents.base import QueryTask, Help
import teamin
from common.cntime import CNTime

import re
import logging

logger = logging.getLogger(__name__)

class IntentQtaskAbout(QueryTask):
    NAME = 'QTASK_ABOUT'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        pskey = self.bestCandidate()
        if not pskey:
            return Help.Response()

        kw = self.parseKeywords(query, pskey)

        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)

        # 双重条件：人物+关键词，时间+关键词
        if hasattr(self, 'cond_p'):
            kw = '与{}有关，{}'.format(self.cond_p, kw)
            (count, finished, expired), weburl = btc.SpecifyKeywords(query, kw)
            self.intent.set_interval(0, 0, weburl)
        elif hasattr(self, 'cond_t'):
            (count, finished, expired), weburl = btc.SpecifyKeywordsTime(query, kw, self.cond_t)
            self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)

    def initSlots(self):
        slots = self.intent.slots.filter(type__startswith='user_').all()
        for slot in slots:
            f = slot.type[5:]
            if f == 'q':
                self.slot_q = slot
            elif f == 'tsk':
                self.slot_tsk = slot
            elif f == 'p':
                self.slot_p = slot
            elif f == 't':
                self.slot_t = slot
            elif f == 't2':
                self.slot_t2 = slot

        if hasattr(self, 'slot_p'):
            self.cond_p = self.slot_p.original_word
        if hasattr(self, 'slot_t'):
            self.cond_t = CNTime(self.slot_t.original_word).guess_time()
            if hasattr(self, 'slot_t2'):
                t2 = CNTime(self.slot_t2.original_word).guess_time()
                self.cond_t = CNTime.Merge(self.cond_t, t2)

    def patterns(self):
        return { 
            'a': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][D:user_p][W:4-99][D:kw_rel][W:0-8]',
            'b': '[D:kw_plz][D:user_q][D:kw_inc][D:user_p][W:4-99][D:kw_rel][D:kw_de][D:user_tsk]',
            'c': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][D:user_p][W:0-8]',
            'd': '[D:kw_plz][D:user_q][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][D:user_p][D:kw_de][D:user_tsk]',
            'e': '[D:kw_plz][D:user_q][D:kw_inc][W:0-2][D:user_t][W:0-8][D:user_t2][W:4-99][D:kw_rel][D:kw_de][D:user_tsk]',
            'f': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][W:0-2][D:user_t][W:0-8][D:user_t2][W:4-99][D:kw_rel][W:0-8]',
            'g': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][D:user_t][W:4-99][D:kw_rel][W:0-8]',
            'h': '[D:kw_plz][D:user_q][D:kw_inc][D:user_t][W:4-99][D:kw_rel][D:kw_de][D:user_tsk]',
            'i': '[D:kw_plz][D:user_q][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][W:0-2][D:user_t][W:0-8][D:user_t2][D:kw_de][D:user_tsk]',
            'j': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][W:0-2][D:user_t][W:0-8][D:user_t2][W:0-8]',
            'k': '[D:kw_plz][D:user_q][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][D:user_t][D:kw_de][D:user_tsk]',
            'l': '[D:kw_plz][D:user_q][D:user_tsk][D:kw_sp][D:kw_inc][W:8-99][D:kw_rel][D:kw_de][D:user_t][W:0-8]',
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
                rmds = re.findall(r'\[D:user_(p|t|t2)\]', v.match_info)
                candidate = v
                continue
            rmds2 = re.findall(r'\[D:user_(p|t|t2)\]', v.match_info)
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

    def parseKeywords(self, oquery, pskey):
        bq = oquery.encode('gbk')

        kw_sp  = self.kws.get('sp')
        kw_inc = self.kws.get('inc')
        s, e = None, None

        if pskey in ['a', 'b']:
            s =  self.slot_p.offset + self.slot_p.length
        elif pskey in ['c']:
            s = self.slot_tsk.offset + self.slot_tsk.length + kw_sp[1] + kw_inc[1]
        elif pskey in ['d']:
            s = self.slot_q.offset + self.slot_q.length + kw_inc[1]
            e = self.slot_p.offset
        elif pskey in ['e', 'f']:
            s = self.slot_t2.offset + self.slot_t2.length
        elif pskey in ['g', 'h']:
            s = self.slot_t.offset + self.slot_t.length
        elif pskey in ['i', 'k']:
            s = self.slot_q.offset + self.slot_q.length + kw_inc[1]
            e = self.slot_t.offset
        elif pskey in ['j', 'l']:
            s = self.slot_tsk.offset + self.slot_tsk.length + kw_sp[1] + kw_inc[1]
            e = self.slot_t.offset

        ret = ''
        if s and e:
            ret = bq[s:e].decode('gbk')
        elif s:
            ret = bq[s:].decode('gbk')
        elif e:
            ret = bq[:e].decode('gbk')

        if ret and ret[0] not in ['与', '和', '跟']:
            ret = '与' + ret
        return ret
