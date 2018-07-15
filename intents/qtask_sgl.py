import time
import logging
from intents.base import QueryTask
from app import matcher
from common.cntime import CNTime
import teamin
logger = logging.getLogger(__name__)


class IntentQtaskSgl(QueryTask):
    NAME = 'QTASK_SINGLE'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        slot = self.intent.slots.filter(type='user_tsk').first()
        keyword = self.parse_keyword(self.intent, query, slot)

        if hasattr(self,'executor'):
            executor = teamin.NameFindNames().ResolveName(self.request.UID(), self.executor)
            (count, finished, expired), weburl = btc.SpecifyExecutors(query, executor)
            self.intent.set_interval(0, 0, weburl)

        elif hasattr(self,'stime') or hasattr(self,'etime'):
            me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
            start = None
            end = None
            if hasattr(self,'stime') and hasattr(self,'etime'):
                s = CNTime(self.stime)
                e = CNTime(self.etime)
                st,en= CNTime.Merge(s.guess_time(),e.guess_time())
                if st == None or en == None:
                    (count, finished, expired), weburl = btc.Deprecated(
                        self.request.UID(),
                        0, 0,
                        query, keyword,
                        matcher.extract_watch(query),
                    )
                    self.intent.set_interval(0, 0, weburl)
                start = st
                end = en

            if hasattr(self,'etime') and not hasattr(self,'stime'):
                # endt:6号到7号
                setime = CNTime(self.etime)
                fromt,tot = setime.guess_time()
                logger.info('raw time {},{}'.format(fromt,tot))
                if fromt == None or tot == None:
                    (count, finished, expired), weburl = btc.Deprecated(
                        self.request.UID(),
                        0, 0,
                        query, keyword,
                        matcher.extract_watch(query),
                    )
                    self.intent.set_interval(0, 0, weburl)
                start = fromt
                end = tot

            logger.info('类型：s:{},e:{}'.format(type(str(start)),type(str(end))))
            logger.info('时间:{}~{}'.format(start,end))
            (count, finished, expired), weburl = btc.SpecifyTime(query,start,end,me)
            if (start != None and end != None):
                self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)
            return self.Response(count, finished, expired, weburl)


        elif hasattr(self,'status'):
            me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
            (count, finished, expired), weburl = btc.SpecifyStatus(query, self.status, me)
            self.intent.set_interval(0, 0, weburl)

        elif hasattr(self,'actions'):
            me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
            (count, finished, expired), weburl = btc.SpecifyActions(query, self.actions, me)
            self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)

    @classmethod
    def parse_keyword(cls, intent, query, slot):
        candidate = intent.candidates.first()
        if not candidate:
            return query
        if '[D:kw_de][D:user_tsk]' in candidate.match_info:
            return cls.cut(query, slot.original_word)
        else:
            word = candidate.match_info.split('kw_de:')[-1]
            return cls.cut(query, word)

    @classmethod
    def cut(cls, sentence, word):
        if not word:
            return sentence

        pos = sentence.find(word)
        if pos == -1:
            return sentence

        sentence = sentence[pos + len(word):]
        while sentence and not sentence[0].isalpha():
            sentence = sentence[1:]

        return sentence


    def initSlots(self):
        # user_q
        # user_sglq_a
        # user_sglq_s
        # user_sglq_t
        # user_sglq_w
        # user_task

        # 查询执行人
        self.slot_w = self.intent.slots.filter(type='user_sglq_w').first()
        if self.slot_w:
            self.executor = self.slot_w.original_word
        else:
            self.me = '我'

        # 查询执行时间
        self.slot_ts = self.intent.slots.filter(type='user_sglq_ts').first()
        if self.slot_ts:
            self.stime = self.slot_ts.original_word

        self.slot_te = self.intent.slots.filter(type='user_sglq_te').first()
        if self.slot_te:
            self.etime = self.slot_te.original_word

        # 查询执行状态
        self.slot_s = self.intent.slots.filter(type='user_sglq_s').first()
        if self.slot_s:
            self.status = self.slot_s.original_word

        # 查询任务行为
        self.slot_a = self.intent.slots.filter(type='user_sglq_a').first()
        if self.slot_a:
            self.actions = self.slot_a.original_word






