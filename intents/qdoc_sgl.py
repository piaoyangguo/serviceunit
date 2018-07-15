import time
import logging
from common.cntime import CNTime
import teamin
from intents.base import QueryDoc
logger = logging.getLogger(__name__)


class IntentQdocSgl(QueryDoc):
    NAME = 'QDOC_SINGLE'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)

        if hasattr(self,'creator'):
            creator = teamin.NameFindNames().ResolveName(self.request.UID(), self.creator)
            count, weburl = bdc.SpecifyCreators(query, creator)
            self.intent.set_interval(0, 0, weburl)

        elif hasattr(self,'stime') or hasattr(self,'etime'):
            me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)

            if hasattr(self,'stime') and hasattr(self,'etime'):
                # 6号和7号
                s = CNTime(self.stime)
                e = CNTime(self.etime)
                start, end = CNTime.Merge(s.guess_time(), e.guess_time())
                # start = str(int(st.timestamp() * 1000))
                # end = str(int(en.timestamp() * 1000))

            if hasattr(self,'etime') and not hasattr(self,'stime'):
                # endt:6号到7号
                time = CNTime(self.etime)
                start, end = time.guess_time()
                logger.info('raw time {},{}'.format(start, end))
                # start = str(int(fromt.timestamp()*1000))
                # end = str(int(tot.timestamp()*1000))

            logger.info('类型：s:{},e:{}'.format(type(str(start)),type(str(end))))
            logger.info('时间戳:{}~{}'.format(start,end))
            count, weburl = bdc.SpecifyTime(query,start,end,me)
            self.intent.set_interval(int(start.timestamp() * 1000), int(end.timestamp() * 1000), weburl)

        elif hasattr(self,'actions'):
            me = teamin.NameFindNames().ResolveName(self.request.UID(), self.me)
            count, weburl = bdc.SpecifyCreators(query, me)
            self.intent.set_interval(0, 0, weburl)

        return self.Response(count, weburl)

    def initSlots(self):
        # user_q
        # user_qdo_a
        # user_qdo_s
        # user_qdo_ts
        # user_qdo_te
        # user_qdo_w

        # 查询执行人
        self.slot_w = self.intent.slots.filter(type='user_qdo_w').first()
        if self.slot_w:
            self.creator = self.slot_w.original_word
        else:
            self.me = '我'

        # 查询执行时间
        self.slot_ts = self.intent.slots.filter(type='user_qdo_ts').first()
        if self.slot_ts:
            self.stime = self.slot_ts.original_word

        self.slot_te = self.intent.slots.filter(type='user_qdo_te').first()
        if self.slot_te:
            self.etime = self.slot_te.original_word

        # 查询文档行为
        self.slot_a = self.intent.slots.filter(type='user_qdo_a').first()
        if self.slot_a:
            self.actions = self.slot_a.original_word






