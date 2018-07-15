import logging
import requests
import random
import time

from serviceunit import settings

logger = logging.getLogger(__name__)

class API():
    base = getattr(settings, 'NAME_BASE')
    timeout = 5

    def __init__(self):
        self.headers = {}


    class Exception(Exception):
        pass


    def JsonResponse(self, res):
        if res.status_code != 200 or  not res.text:
            msg = 'Reqeust Namerecog failure, code={}, res={}'.format(res.status_code, res.text)
            logger.info(msg)
            raise self.Exception(msg, res)

        try:
            return res.json(), res
        except Exception as e:
            msg = 'Reqeust Namerecog failure(invalid json), res={}'.format(res.text)
            logger.info(msg)
            raise self.Exception(msg, res)


    def Get(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = self.base + api
        res = requests.get(url, params=params, headers=h, timeout=self.timeout)
        msg = 'GET Namerecog, api={}, params={}, headers={}'.format(api, params, h)
        logger.debug(msg)
        return self.JsonResponse(res)


    def Post(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = self.base + api
        res = requests.post(url, data=params, headers=h, timeout=self.timeout)
        msg = 'POST Namerecog, api={}, params={}, headers={}'.format(api, params, h)
        logger.debug(msg)
        return self.JsonResponse(res)


class ApiFindNames(API):
    cache = {}
    rcache = {}
    ids = {'nid': -1, 'last_uid': 0}

    def __init__(self):
        super().__init__()

        # doc: http://git.teamin.cc:4999/index.php?s=/4&page_id=118
        self.api = '/v1/findnames'


    def Do(self, params={}):
        #params = {
        #    'names': '',
        #    'uid': 0,
        #    'cid': 0,
        #}

        res, _ = self.Post(self.api, params)

        return res


    def ResolveNames(self, uid, *names):
        params = {
            'uid': uid,
            'names': ','.join(names),
        }
        ret = self.Do(params)
        logger.debug('resolve names {}({}) => {}'.format(uid, names, ret))
        self.ids['last_uid'] = uid
        return ret


    def ResolveName(self, uid, name):
        x = self.searchCache(uid, name)
        if x != None:
            return x

        res = self.ResolveNames(uid, name)
        if name in res:
            ret = res[name]['uid']
        else:
            ret = self.ids['nid']
            self.ids['nid'] -= 1

        self.storeCache(uid, name, ret)

        return ret

    def searchCache(self, uid, name):
        self.cleanCache()
        key = '{}-{}'.format(uid, name)
        x = self.cache.get(key, None)
        if x:
            x = x[0]
        return x

    def storeCache(self, uid, name, ret):
        self.cleanCache()
        key = '{}-{}'.format(uid, name)
        rkey = '{}-{}'.format(uid, ret)
        now = int(time.time())
        self.cache[key] = (ret, now + 600, rkey)
        self.rcache[rkey] = name

    def cleanCache(self):
        # 1% 概率触发cache清理
        if random.randint(0, 99) > 0:
            return
        now = int(time.time())
        for k in list(self.cache):
            _, expired, rkey = self.cache[k]
            if now > expired:
                try:
                    self.cache.pop(k)
                    self.rcache.pop(rkey)
                except Exception:
                    pass

    def ResolveUID(self, tgtuid, uid=0):
        self.cleanCache()
        if not uid:
            uid = self.ids['last_uid']
        rkey = '{}-{}'.format(uid, tgtuid)
        return self.rcache.get(rkey, None)
