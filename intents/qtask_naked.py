from intents.base import QueryTask
import teamin

class IntentQtaskNaked(QueryTask):
    NAME = 'QTASK_NAKED'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        if self.request.Session:
            return self.GoWithSession()

        return self.ResponseNaked(self.request.Message(), self.request.UID())
    
    def GoWithSession(self):
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        (count, finished, expired), weburl = btc.SpecifyKeywords(query, query)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)
