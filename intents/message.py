from intents.base import Message

class IntentMessage(Message):
    NAME = 'UNKNOWN'

    def __init__(self, message):
        self.message = message

    def Go(self):
        return self.Response(self.message)
