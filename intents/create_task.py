from intents.base import CreateTask

class IntentCreateTask(CreateTask):
    NAME = 'CREATE_TASK'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        msg = self.parse()

        if len(msg) < 2:
            return self.ResponseNaked(self.request.Message(), self.request.UID())

        return self.Response(msg)

    def parse(self):
        query = self.request.Message()
        slot = self.intent.slots.filter(type='user_task').first()
        candidate = self.intent.candidates.first()
        original_word = slot.original_word
        if candidate and candidate.match_info and '[D:kw_new][W:0-100][D:user_task]' in candidate.match_info:
            kw_val = self.extract_match_info(candidate.match_info, 'kw_new')
            if kw_val:
                original_word = kw_val
        return self.cut(query, original_word)

    @classmethod
    def extract_match_info(match_info, kw):
        """[D:kw_please][D:kw_new][W:0-100][D:user_task] kw_please:给我|kw_new:创建"""
        kw_list = match_info.split()[-1]
        if kw_list:
            for kw_str in kw_list.split('|'):
                if kw in kw_str:
                    return kw_str.split(':')[-1]
        return ''

    @classmethod
    def cut(cls, sentence, word):
        if not word:
            return sentence

        pos = sentence.find(word)
        if pos == -1: 
            return sentence

        sentence = sentence[pos + len(word):]
        while sentence and not sentence[0].isalpha():
            sentence = sentence[1:]

        return sentence

