from intents.base import QuerySettingRemind 
from intents.help2 import IntentHelp2

class IntentQsetRemind(QuerySettingRemind):
    NAME = 'QSET_REMIND'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        slots = self.intent.slots.filter(type__startswith='user_').all()
        for slot in slots:
            if 'user_hlp_' == slot.type[:9]:
                return IntentHelp2(self.request, self.intent).Go()

        return self.Response(self.request.Message())
