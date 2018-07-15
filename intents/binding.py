from intents.base import Binding

class IntentBinding(Binding):
    NAME = 'BINDING'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response(self.request.Message())
