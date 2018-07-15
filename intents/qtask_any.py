from intents.base import QueryTask
import teamin

class IntentQtaskAny(QueryTask):
    NAME = 'QTASK_ANY'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        query = self.request.Message()

        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        (count, finished, expired), weburl = btc.All(query)
        self.intent.set_interval(0, 0, weburl)

        return self.Response(count, finished, expired, weburl)
