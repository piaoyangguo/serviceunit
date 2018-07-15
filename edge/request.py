import edge
import teamin
import baidu.bce as bce

class Request():
    Agent_WECHAT = 1
    Agent_WXOA   = 2

    QType_TEXT   = 1
    QType_VOICE  = 2


    def __init__(self, query):
        if type(query) == str:
            self.QType = self.QType_TEXT
            self.Query = query
        else:
            self.QType = self.QType_VOICE
            self.Query = query


    def InitAgent(self, name, id):
        if name == 'WXOA':
            self.Agent = self.Agent_WXOA
        else:
            self.Agent = self.Agent_WECHAT

        self.AgentName = name
        self.AgentUID  = id
        return self

    
    def InitSession(self, session):
        self.Session = None
        if session:
            s = edge.Session.Unserialize(session)
            if s and s.Verify(self.UID()):
                self.Session = s
        return self


    def UID(self, useCache=True):
        if useCache:
            uid = getattr(self, '_uid', 0)
            if uid:
                return uid

        # transform agent uid to teamin uid
        self._uid = teamin.BizBindInfo().TeaminUID(self.AgentName, self.AgentUID)
        return self._uid


    def Message(self, useCache=True):
        if self.QType == self.QType_TEXT:
            return self.Query
        if self.QType == self.QType_VOICE:
            if useCache:
                query = getattr(self, '_voice_text', '')
                if query:
                    return query

            # transform voice to text
            cuid = '{}-{}'.format(self.AgentName, self.AgentUID)
            self._voice_text = bce.BCE().ASR(cuid, self.Query)
            return self._voice_text
