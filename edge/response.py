import edge

from teamin import web

class Response():
    Intent_UNKNOWN     = -1
    Intent_CREATE_TASK = 1
    Intent_QUERY_TASK  = 2
    Intent_QUERY_DOC   = 4
    Intent_HELP        = 5
    Intent_REMIND      = 6
    Intent_BINDING     = 7

    Intent_QUERY_SETTING_REMIND = 8


    def __init__(self, intent, unitIntent=''):
        self.Intent = intent
        self.UnitIntent = unitIntent
        self.Session = None
        self.Eve = True


    def InitMessage(self, message, url=web.URL(), gurl=web.URL()):
        self.Message = message
        self.URL = url
        self.GURL = gurl
        return self


    def SetSession(self, rawQuery, uid=0, payload=None):
        s = edge.Session(self.Intent, uid)
        s.Payload = {
            'query': rawQuery,
            'data': payload,
        }

        self.UseSession(s)


    def UseSession(self, session):
        self.Session = session
        self.Eve = False

   
    def FormatDict(self):
        return {
            'intent': self.Intent,
            'session': self.Session.Serialize(),
            'message': self.Message,
            'url': self.URL,
            'gurl': self.GURL,
            'eve': self.Eve,
        }
