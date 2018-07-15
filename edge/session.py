import time, base64

import msgpack

class Session():
    ExpireIn = 300

    # ExpireIn = 30000000000

    def __init__(self, intent, uid=0):
        self.Intent  = intent
        self.UID     = uid

        self.Payload = {}
        self.Access  = time.time()


    def SetPayload(self, rawQuery, payload=None):
        self.Payload['query'] = rawQuery
        self.Payload['data'] = payload


    def GetPayload(self):
        return self.Payload.get('query', ''), self.Payload.get('data', None)


    def Verify(self, uid=0):
        now = time.time()
        if self.Access + self.ExpireIn < now:
            # expired
            return False
        return self.UID == uid


    def Serialize(self):
        self.Access = time.time()
        data = (self.Intent, self.UID, self.Payload, self.Access)
        mb = msgpack.packb(data)
        return base64.b64encode(mb).decode('ascii')


    @classmethod
    def Unserialize(cls, string):
        try:
            b64  = base64.b64decode(string)
            data = msgpack.unpackb(b64, encoding='utf-8', use_list=False)
        except Exception as e:
            print('invalid session string')
            return None
        s = Session(data[0], data[1])
        s.Payload = data[2]
        s.Access = data[3]
        return s
