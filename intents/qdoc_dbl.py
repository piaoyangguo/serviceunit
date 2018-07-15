import time
import logging
from intents.base import QueryDoc
from app import matcher
from common.cntime import CNTime
import teamin
logger = logging.getLogger(__name__)


class IntentQdocDbl(QueryDoc):
    NAME = 'QDOC_DB'

    def Go(self):
        self.initSlots()
        # 1 谁+时间
        if hasattr(self, 'executor') and (hasattr(self, 'stime') or hasattr(self, 'etime')):
            return self.intents_who_time()
        # 2 时间+行为
        if (hasattr(self, 'stime') or hasattr(self, 'etime')) and hasattr(self, 'actions'):
            return self.intents_time_actions()

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def initSlots(self):
        # user_upl_u
        # user_db_te
        # user_db_ts
        # user_db_w
        # user_doc
        # user_q

        # 查询执行人
        self.slot_w = self.intent.slots.filter(type='user_db_w').first()
        if self.slot_w:
            self.executor = self.slot_w.original_word
        else:
            self.me = '我'

        # 查询执行时间
        self.slot_ts = self.intent.slots.filter(type='user_db_ts').first()
        if self.slot_ts:
            self.stime = self.slot_ts.original_word

        self.slot_te = self.intent.slots.filter(type='user_db_te').first()
        if self.slot_te:
            self.etime = self.slot_te.original_word

        # 查询任务行为
        self.slot_a = self.intent.slots.filter(type='user_upl_u').first()
        if self.slot_a:
            self.actions = self.slot_a.original_word

    def intents_time_actions(self):
        # 5 时间+行为
        query = self.request.Message()
        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
        start = None
        end = None
        if hasattr(self, 'stime') and hasattr(self, 'etime'):
            s = CNTime(self.stime)
            e = CNTime(self.etime)
            st, en = CNTime.Merge(s.guess_time(), e.guess_time())
            logger.info('raw time {},{}'.format(st, en))
            start, end = st, en
        if hasattr(self, 'etime') and not hasattr(self, 'stime'):
            time = CNTime(self.etime)
            fromt, tot = time.guess_time()
            logger.info('raw time {},{}'.format(fromt, tot))
            start, end = fromt, tot

        (count, weburl) = bdc.SpecifyDblSelect(query,
                                               me,
                                               stime=start,
                                               etime=end,
                                               actions=self.actions)
        self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)
        return self.Response(count, weburl)

    def intents_who_time(self):
        # 2 谁+时间
        query = self.request.Message()
        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        executors = teamin.NameFindNames().ResolveName(self.request.UID(), self.executor)
        start = None
        end = None
        if hasattr(self, 'stime') and hasattr(self, 'etime'):
            s = CNTime(self.stime)
            e = CNTime(self.etime)
            st, en = CNTime.Merge(s.guess_time(), e.guess_time())
            logger.info('raw time {},{}'.format(st, en))
            start,end = st,en

        if hasattr(self, 'etime') and not hasattr(self, 'stime'):
            time = CNTime(self.etime)
            fromt, tot = time.guess_time()
            logger.info('raw time {},{}'.format(fromt, tot))
            start, end = fromt, tot

        (count, weburl) = bdc.SpecifyDblSelect(query,
                                                executors,
                                                stime=start,
                                                etime = end,
                                                executors=executors)
        self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)
        return self.Response(count, weburl)

