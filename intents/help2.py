from intents.base import Help

class IntentHelp2(Help):
    NAME = 'HELP2'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response()
