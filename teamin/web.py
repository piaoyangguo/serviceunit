import logging
import json
import teamin

from urllib.parse import urlencode

from serviceunit import settings

logger = logging.getLogger(__name__)

class URL():
    base = getattr(settings, 'H5_BASE')

    def __init__(self, page='', params={}, count=0, result={}):
        self.page = page
        self.params = params
        self.count = count

        self.result = {}
        self.names = {}
        self.nlp = {}
        self.extra = {}

        for k in ['fileCount', 'taskCount', 'finishTaskCount', 'expireTaskCount']:
            if k in result:
                self.result[k] = result[k]

        k = 'nlp_about'
        if k in params:
            x = {v['userName']: v['userId'] for v in params.pop(k)}
            if x:
                self.nlp['about'] = x
        k = 'nlp_keywords'
        if k in params:
            x = params.pop(k)
            if x:
                self.nlp['keywords'] = x

        ks = ['filterAssigners', 'filterClosers', 'filterCreators', 'filterCreaters']
        for k in ks:
            if k in params:
                self.names[k] = self.getNames(params[k])
        k = 'filterAttentions'
        if k in params:
            x = json.loads(params[k])
            self.names[k] = self.getNames([int(v['userId']) for v in x])
            self.extra[k] = x

    def Add(self, key, value):
        self.params[key] = value

    def Del(self, key):
        self.params.pop(key)

    def Params(self):
        return self.params

    def Result(self):
        return self.result

    def NLP(self):
        return self.nlp

    def Names(self):
        return self.names

    def Extra(self):
        return self.extra

    def getNames(self, ids):
        if type(ids) == str:
            ids = [int(v) for v in ids.split(',') if v]
        x = {}
        for v in ids:
            y = teamin.NameFindNames().ResolveUID(v)
            if y:
                x[y] = v
        return x

    def __str__(self):
        if self.count == 0:
            return ''
        params = self.params.copy()
        return '{}{}?{}'.format(
            self.base, self.page, urlencode(params),
        )

def UrlQueryTask(params, count, result):
    page = '/h5/job-summary'
    return URL(page, params, count, result)

def UrlQueryDoc(params, count, result):
    page = '/h5/document'
    return URL(page, params, count, result)
