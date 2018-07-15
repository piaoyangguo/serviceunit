import logging
import requests
import time

from serviceunit import settings
from urllib.parse import urlencode
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class BCE():
    base = 'https://aip.baidubce.com'
    timeout = 5
    apiKey = getattr(settings, 'UNIT_API_KEY')
    secretKey = getattr(settings, 'UNIT_SECRET_KEY')

    def __init__(self):
        self.headers = {}


    class Exception(Exception):
        pass


    def JsonResponse(self, res):
        if res.status_code != 200 or  not res.text:
            msg = 'Reqeust BCE failure, code={}, res={}'.format(res.status_code, res.text)
            logger.info(msg)
            raise self.Exception(msg, res)

        try:
            j = res.json()
        except Exception as e:
            msg = 'Reqeust BCE failure(invalid json), res={}'.format(res.text)
            logger.info(msg)
            raise self.Exception(msg, res)

        if 'error' not in j:
            return j, res
        msg = 'Request BCE failure(error), res={}'.format(res.text)
        logger.info(msg)
        raise self.Exception(msg, res)

    
    def Get(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = self.base + api
        params['access_token'] = self.GetToken()
        res = requests.get(url, params=params, headers=h, timeout=self.timeout)
        msg = 'GET BCE, api={}, params={}, headers={}'.format(api, params, h) 
        logger.debug(msg)
        return self.JsonResponse(res)

    
    def Json(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = '{}{}?access_token={}'.format(self.base, api, self.GetToken())
        res = requests.post(url, json=params, headers=h, timeout=self.timeout)
        msg = 'JSON BCE, api={}, params={}, headers={}'.format(api, params, h) 
        logger.debug(msg)
        return self.JsonResponse(res)


    def GetToken(self):
        token = getattr(self, '_token', ())
        if token and token[2] > time.time():
            return token[0]
        token, _ = self.AccessToken()
        return token


    def AccessToken(self):
        api = '/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.apiKey,
            'client_secret': self.secretKey,
        }

        url = self.base + api
        res = requests.get(url, params=params, timeout=self.timeout)
        res, _ = self.JsonResponse(res)

        self._token = (res['access_token'], res['expires_in'], time.time() + res['expires_in'] - 86400)

        return res['access_token'], res['expires_in']


    def UNIT(self, scene_id, query):
        api = '/rpc/2.0/solution/v1/unit_utterance'
        params = {
            'scene_id': scene_id,
            'query': query,
            #'session_id': '',
        }

        res, _ = self.Json(api, params)
        return res


    def ASR(self, uid, file_obj):
        url = '{}?{}'.format(
            'https://vop.baidu.com/server_api',
            urlencode({'token': self.GetToken(), 'cuid': uid}),
        )
        headers = {'Content-Type': 'audio/wav;rate=8000'}

        data = AudioSegment.from_file(file_obj).raw_data

        res = requests.post(url, data=data, headers=headers)
        res, _ = self.JsonResponse(res)
        if res['result']:
            return res['result'][0]
        return ''
