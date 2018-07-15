from intents.base import QueryTask, QueryDoc
import teamin

from app import matcher

class IntentViewTask(QueryTask):
    NAME = 'VIEW_TASK'

    def __init__(self, request, intent):
        self.request = request
        self.intent = intent

    def Go(self):
        query = self.request.Message()
        slot = self.intent.slots.filter(type='user_task').first()
        keyword = self.parse_keyword(self.intent, query, slot)

        start, end = 0, 0
        for slot_t in self.intent.slots.filter(type='user_time'):
            start, end = matcher.parse_time(query, slot_t.original_word, slot_t.normalized_word)
            if start and end:
                break
        if matcher.match_file_keyword(slot.original_word):
            return self.view_file(start, end, keyword)
        else:
            return self.view_task(start, end, keyword)

    @classmethod
    def parse_keyword(cls, intent, query, slot):
        candidate = intent.candidates.first()
        if not candidate:
            return query
        if '[D:kw_view][D:user_task]' in candidate.match_info:
            return cls.cut(query, slot.original_word)
        else:
            word = candidate.match_info.split('kw_view:')[-1]
            return cls.cut(query, word)

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

    def view_file(self, start, end, keyword):
        query = self.request.Message()
        bdc = teamin.BizDocCount(self.request.AgentName, self.request.AgentUID)
        count, weburl = bdc.Deprecated(start, end, query, keyword)
        self.intent.set_interval(start, end, weburl)

        return QueryDoc.Response(count, weburl)

    def view_task(self, start, end, keyword):
        query = self.request.Message()
        btc = teamin.BizTaskCount(self.request.AgentName, self.request.AgentUID)
        (count, finished, expired), weburl = btc.Deprecated(
            self.request.UID(),
            start, end,
            query, keyword,
            matcher.extract_watch(query),
        )
        self.intent.set_interval(start, end, weburl)

        return self.Response(count, finished, expired, weburl)
