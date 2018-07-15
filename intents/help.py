from intents.base import Help

class IntentHelp(Help):
    NAME = 'HELP'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        return self.Response()
