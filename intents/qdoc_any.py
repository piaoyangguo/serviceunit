from intents.base import QueryDoc
import teamin

class IntentQdocAny(QueryDoc):
    NAME = 'QDOC_ANY'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        query = self.request.Message()

        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        count, weburl = bdc.All(query)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, weburl)
