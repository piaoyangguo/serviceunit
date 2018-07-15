from intents.base import QueryTask
import teamin

class IntentQtaskExec(QueryTask):
    NAME = 'QTASK_EXEC'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        executor = teamin.NameFindNames().ResolveName(self.request.UID(), self.executor)

        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        (count, finished, expired), weburl = btc.SpecifyExecutors(query, executor)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)

    def initSlots(self):
        self.slot_w = self.intent.slots.filter(type='user_qte_w').first()
        self.executor = self.slot_w.original_word
