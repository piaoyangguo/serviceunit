from intents.base import QueryDoc
import teamin

class IntentQdocNaked(QueryDoc):
    NAME = 'QDOC_NAKED'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        if self.request.Session:
            return self.GoWithSession()

        return self.ResponseNaked(self.request.Message(), self.request.UID())
    
    def GoWithSession(self):
        query = self.request.Message()
        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        count, weburl = bdc.SpecifyKeywords(query, query)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, weburl)
