from intents.base import QueryDoc
import teamin

class IntentQdocCrt(QueryDoc):
    NAME = 'QDOC_CRT'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        self.initSlots()
        query = self.request.Message()
        creator = teamin.NameFindNames().ResolveName(self.request.UID(), self.creator)

        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        count, weburl = bdc.SpecifyCreators(query, creator)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, weburl)

    def initSlots(self):
        self.slot_w = self.intent.slots.filter(type='user_qdc_w').first()
        self.creator = self.slot_w.original_word
