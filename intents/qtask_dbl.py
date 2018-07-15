import time
import logging
from intents.base import QueryTask
from app import matcher
from common.cntime import CNTime
import teamin
logger = logging.getLogger(__name__)


class IntentQtaskDbl(QueryTask):
    NAME = 'QTASK_DB'

    def Go(self):
        self.initSlots()
        # 1 谁+状态
        if hasattr(self, 'executor') and hasattr(self, 'status'):
            return self.intents_who_st()
        # 2 谁+时间
        if hasattr(self, 'executor') and (hasattr(self, 'stime') or hasattr(self, 'etime')):
            return self.intents_who_time()
        # 3 谁+行为
        if hasattr(self, 'executor') and (hasattr(self, 'actions') or hasattr(self, 'slot_cr')):
            return self.intents_who_actions()
        # 4 时间+状态
        if (hasattr(self, 'stime') or hasattr(self, 'etime')) and hasattr(self, 'status'):
            return self.intents_time_st()
        # 5 时间+行为
        if (hasattr(self, 'stime') or hasattr(self, 'etime')) and hasattr(self, 'actions'):
            return self.intents_time_actions()
        # 6 状态+行为
        if hasattr(self, 'status') and hasattr(self, 'actions'):
            return self.intents_st_actions()

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def initSlots(self):
        # user_db_cr
        # user_db_st
        # user_db_a
        # user_db_te
        # user_db_ts
        # user_db_w
        # user_tsk
        # user_q

        # 查询创建er
        self.slot_cr = self.intent.slots.filter(type='user_db_cr').first()
        if self.slot_cr:
            self.slot_cr = self.slot_cr.original_word

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

        # 查询执行状态
        self.slot_s = self.intent.slots.filter(type='user_db_st').first()
        if self.slot_s:
            self.status = self.slot_s.original_word

        # 查询任务行为
        self.slot_a = self.intent.slots.filter(type='user_db_a').first()
        if self.slot_a:
            self.actions = self.slot_a.original_word

    def intents_st_actions(self):
        # 6 状态+行为
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
        (count, finished, expired), weburl = btc.SpecifyDblSelect(query, me, status=self.status,actions=self.actions)
        self.intent.set_interval(0, 0, weburl)
        return self.Response(count, finished, expired, weburl)

    def intents_time_actions(self):
        # 5 时间+行为
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
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

        (count, finished, expired), weburl = btc.SpecifyDblSelect(query,
                                                                  me,
                                                                  stime=start,
                                                                  etime=end,
                                                                  actions=self.actions)
        if (start != None and end != None):
            self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)
        return self.Response(count, finished, expired, weburl)

    def intents_time_st(self):
        # 4 时间+状态
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
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

        (count, finished, expired), weburl = btc.SpecifyDblSelect(query,
                                                                  me,
                                                                  stime=start,
                                                                  etime=end,
                                                                  status=self.status)
        if(start != None and end != None):
            self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)

        return self.Response(count, finished, expired, weburl)


    def intents_who_actions(self):
        # 3 谁+行为
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        executors = teamin.NameFindNames().ResolveName(self.request.UID(), self.executor)
        if self.slot_cr:
            act = '创建'
        else:
            act = self.actions
        (count, finished, expired), weburl = btc.SpecifyDblSelect(query, executors, actions=act, executors=executors)
        self.intent.set_interval(0, 0, weburl)
        return self.Response(count, finished, expired, weburl)

    def intents_who_time(self):
        # 2 谁+时间
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
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

        (count, finished, expired), weburl = btc.SpecifyDblSelect(query,
                                                                  executors,
                                                                  stime=start,
                                                                  etime = end,
                                                                  executors=executors)
        if (start != None and end != None):
            self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)
        return self.Response(count, finished, expired, weburl)



    def intents_who_st(self):
        # 1 谁+状态
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        executors = teamin.NameFindNames().ResolveName(self.request.UID(), self.executor)
        (count, finished, expired), weburl = btc.SpecifyDblSelect(query,executors,status=self.status,executors=executors)
        self.intent.set_interval(0, 0, weburl)
        return self.Response(count, finished, expired, weburl)
