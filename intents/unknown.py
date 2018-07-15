from intents.base import Unknown

class IntentUnknown(Unknown):
    NAME = 'UNKNOWN'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response()
