from intents.base import QueryTask
import teamin

class IntentQtaskFos(QueryTask):
    NAME = 'QTASK_FOS'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        follower = teamin.NameFindNames().ResolveName(self.request.UID(), self.follower)

        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        (count, finished, expired), weburl = btc.SpecifyFollowers(query, follower)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)

    def initSlots(self):
        self.slot_w = self.intent.slots.filter(type='user_qtf_w').first()
        self.follower = self.slot_w.original_word
