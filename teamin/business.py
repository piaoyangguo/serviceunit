import json
import logging
import requests
from math import ceil, floor

import time

from teamin import web
from serviceunit import settings
from common.cntime import CNTime

logger = logging.getLogger(__name__)

class API():
    base = getattr(settings, 'TEAMIN_BASE')
    timeout = 5


    def __init__(self, agent='', agentuid=''):
        self.headers = {}
        self.AgentName = agent
        self.AgentUID = agentuid
        self.initHeaders()


    def initHeaders(self):
        if not (self.AgentName and self.AgentUID):
            return

        if self.AgentName == 'WECHAT':
            self.headers['X-Assistant-Uid'] = self.AgentUID
        elif self.AgentName == 'WXOA':
            self.headers['X-WechatMP-OpenId'] = self.AgentUID


    class Exception(Exception):
        pass


    def JsonResponse(self, res):
        if res.status_code != 200 or  not res.text:
            msg = 'Reqeust Business failure, code={}, res={}'.format(res.status_code, res.text)
            logger.info(msg)
            raise self.Exception(msg, res)

        try:
            return res.json(), res
        except Exception as e:
            msg = 'Reqeust Business failure(invalid json), res={}'.format(res.text)
            logger.info(msg)
            raise self.Exception(msg, res)


    def Get(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = self.base + api
        res = requests.get(url, params=params, headers=h, timeout=self.timeout)
        msg = 'GET Business, api={}, params={}, headers={}'.format(api, params, h)
        logger.debug(msg)
        return self.JsonResponse(res)


    def Post(self, api, params={}, headers={}):
        if headers:
            h = headers
        else:
            h = self.headers.copy()

        url = self.base + api
        res = requests.post(url, data=params, headers=h, timeout=self.timeout)
        msg = 'POST Business, api={}, params={}, headers={}'.format(api, params, h)
        logger.debug(msg)
        return self.JsonResponse(res)



class ApiTaskCount(API):
    def __init__(self, agent='', agentuid=''):
        super().__init__(agent, agentuid)

        # doc: http://git.teamin.cc:4999/index.php?s=/4&page_id=110
        self.api = '/v1/weixin/assistant/circles/tasks/count/ai'


    def Do(self, params={}):
        #params = {
        #    'timeType': '',
        #    'startTime': '',
        #    'endTime': '',
        #    'filterAssOigners': '',
        #    'filterClosers': '',
        #    'closerList': '',
        #    'circleNameFilter': '',
        #    'contentFilter': '',
        #    'srcInput': '',
        #}

        res, _ = self.Get(self.api, params)


        count = res.get('taskCount', 0)
        finished = res.get('finishTaskCount', 0)
        expired = res.get('expireTaskCount', 0)

        # if count == 0:
        #     params = {
        #         'srcInput': params['srcInput'],
        #     }
        params['nlp_about'] = res.get('aboutUsers', [])
        params['nlp_keywords'] = res.get('keywords', [])
        return (count, finished, expired), web.UrlQueryTask(params, count, res)


    def All(self, order):
        params = {
            'srcInput': order,
            'contentFilter': order,
        }
        return self.Do(params)


    def Deprecated(self, myuid, starttime, endtime, order, keyword, watch=None):
        params = {
            'srcInput': order,
            'contentFilter': keyword,
        }
        if starttime > 0 and endtime > 0:
            # 1:截止时间 2:创建时间
            params['timeType'] = 1
            params['startTime'] = starttime
            params['endTime'] = endtime
        if watch:
            params['filterAttentions'] = myuid

        return self.Do(params)


    def SpecifyDblSelect(self, order, *executors, **opr_dict):

        params = {
            'srcInput': order,
        }

        # 1 谁+状态
        if opr_dict.get('status',None) != None and opr_dict.get('executors',None) !=  None:

            # 状态填充
            status_partten = ['未', '待', '没有', '尚未', '还没有', '没']
            left_status = [i for i in status_partten if i in opr_dict.get('status')]
            statusid = 0 if len(left_status) else 3
            # 判断是否过期
            isExpire = self.JudgeStatusExpired(opr_dict.get('status'), status_partten)
            if isExpire == 1:
                logger.info('未过期')
                _starttime = int(time.time())
                params['startTime'] = floor(_starttime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['startTime']))

            elif isExpire == 0:
                logger.info('已过期')
                _endtime = int(time.time())
                params['endTime'] = ceil(_endtime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['endTime']))

            else:
                params['stateId'] = statusid

            real_act = 'filterAssigners'  # self.getActionRole(opr_dict.get('status'))
            params[real_act] = ','.join([str(v) if v > 0 else str(-1) for v in executors]) \
                if real_act != 'filterAttentions' else \
                json.dumps([{
                    "userId": executors[0]  # 当前场景下暂只支持一个关注人。
                }])

            # params['filterAssigners'] = ','.join([str(v) if v > 0 else str(-1) for v in executors])
            logger.info('PARAMS:{}'.format(params))
            return self.Do(params)
        # 2 谁+时间
        if (opr_dict.get('stime','') != '' or opr_dict.get('etime','') != '') and  opr_dict.get('executors','') != '':

            if opr_dict.get('stime', '') != '':
                if opr_dict['stime'] != None:
                    params['startTime'] = floor(opr_dict.get('stime').timestamp() * 1000)
                    params['timeType'] = 1
            if opr_dict.get('etime','') != '':
                if opr_dict['etime'] != None:
                    params['endTime'] = ceil(opr_dict.get('etime').timestamp() * 1000)
                    params['timeType'] = 1

            if opr_dict['stime'] == None and opr_dict['etime'] == None:
                return self.All(order)

            params['filterAssigners'] = ','.join([str(v) if v > 0 else str(-1) for v in executors])
            logger.info('PARAMS:{}'.format(params))
            return self.Do(params)
        # 3 谁+行为
        if opr_dict.get('actions',None) != None and  opr_dict.get('executors',None)!= None:
            return self.SpecifyActions(order,opr_dict.get('actions'),*executors)
        # 4 时间+状态
        if (opr_dict.get('stime','') != '' or opr_dict.get('etime','') != '') and  opr_dict.get('status',None)!= None:
            if opr_dict.get('stime', '') != '':
                if opr_dict['stime'] != None:
                    params['startTime'] = floor(opr_dict.get('stime').timestamp() * 1000)
                    params['timeType'] = 1
            if opr_dict.get('etime','') != '':
                if opr_dict['etime'] != None:
                    params['endTime'] = ceil(opr_dict.get('etime').timestamp() * 1000)
                    params['timeType'] = 1

            if opr_dict['stime'] == None and opr_dict['etime'] == None:
                return self.All(order)

            # 状态填充
            status_partten = ['未', '待', '没有', '尚未', '还没有', '没']
            left_status = [i for i in status_partten if i in opr_dict.get('status')]
            statusid = 0 if len(left_status) else 3
            # 判断是否过期
            isExpire = self.JudgeStatusExpired(opr_dict.get('status'), status_partten)
            if isExpire == 1:
                logger.info('未过期')
                _starttime = int(time.time())
                params['startTime'] = floor(_starttime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['startTime']))

            elif isExpire == 0:
                logger.info('已过期')
                _endtime = int(time.time())
                params['endTime'] = ceil(_endtime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['endTime']))

            else:
                params['stateId'] = statusid

            logger.info('ST&ACT PARAMS:{}'.format(params))
            return self.Do(params)
        # 5 时间+行为
        if (opr_dict.get('stime','') != '' or opr_dict.get('etime','') != '') and  opr_dict.get('actions',None)!= None:
            timetype = {
                'filterClosers':3,
                'filterAssigners':1,
                'filterCreators':2
            }

            real_act = self.getActionRole(opr_dict.get('actions'))
            params[real_act] = ','.join([str(v) if v > 0 else str(-1) for v in executors]) \
                if real_act != 'filterAttentions' else \
                json.dumps([{"startTime": floor(opr_dict.get('stime').timestamp() * 1000),
                  "endTime": ceil(opr_dict.get('etime').timestamp() * 1000),
                  "userId": executors[0] #当前场景下暂只支持一个关注人。
                  }])

            if opr_dict.get('stime', '') != '':
                if opr_dict['stime'] != None:
                    if real_act != 'filterAttentions':
                        params['startTime'] = floor(opr_dict.get('stime').timestamp() * 1000)
                        params['timeType'] = timetype.get(real_act, 1)
            if opr_dict.get('etime','') != '':
                if opr_dict['etime'] != None:
                    if real_act != 'filterAttentions':
                        params['endTime'] = ceil(opr_dict.get('etime').timestamp() * 1000)
                        params['timeType'] = timetype.get(real_act, 1)

            if opr_dict['stime'] == None and opr_dict['etime'] == None:
                return self.All(order)

            logger.info('ST&ACT PARAMS:{}'.format(params))
            return self.Do(params)
        # 6 状态+行为
        if opr_dict.get('status',None) != None and  opr_dict.get('actions',None)!= None:
            # 行为填充
            real_act = self.getActionRole(opr_dict.get('actions'))
            params[real_act] = ','.join([str(v) if v > 0 else str(-1) for v in executors]) \
                if real_act != 'filterAttentions' else \
                json.dumps([{
                    "userId": executors[0]  # 当前场景下暂只支持一个关注人。
                }])
            # 状态填充
            status_partten = ['未', '待', '没有', '尚未', '还没有', '没']
            left_status = [i for i in status_partten if i in opr_dict.get('status')]
            statusid = 0 if len(left_status) else 3
            # 判断是否过期
            isExpire = self.JudgeStatusExpired(opr_dict.get('status'), status_partten)
            if isExpire == 1:
                logger.info('未过期')
                _starttime = int(time.time())
                params['startTime'] = floor(_starttime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['startTime']))

            elif isExpire == 0:
                logger.info('已过期')
                _endtime = int(time.time())
                params['endTime'] = ceil(_endtime * 1000)
                params['timeType'] = 1
                logger.info('{}'.format(params['endTime']))

            else:
                params['stateId'] = statusid

            logger.info('ST&ACT PARAMS:{}'.format(params))
            return self.Do(params)


    def SpecifyTime(self, order, starttime, endtime, *executors):
        params = {
            'srcInput': order,
            'filterAssigners': ','.join([str(v) if v > 0 else str(-1) for v in executors]),
            'timeType': 1,
        }

        if starttime is not None:
            params['startTime'] = floor(starttime.timestamp()*1000)

        if endtime is not None:
            params['endTime'] = ceil(endtime.timestamp()*1000)

        logger.info('TIME PARAMS:{}'.format(params))
        return self.Do(params)


    def getActionRole(self,actions):

        #完成
        done=['完成','完毕','就位']
        #执行
        exec=['执行','操作','处理']
        #关注
        atte = ['关注', '关心']
        #创建
        cret=['创建','建立','新建','新增']

        real_act = ''
        action_partten = {
            'filterClosers':done,
            'filterAssigners':exec,
            'filterAttentions':atte,
            'filterCreators':cret,
        }

        for action_tu in action_partten.items():
            for action_li in action_tu[1]:
                if action_li in actions:
                    real_act = action_tu[0]
                    return real_act

        return real_act
    def SpecifyActions(self, order, actions,*executors):

        real_act = self.getActionRole(actions)

        params = {
            'srcInput': order,
            real_act: ','.join([str(v) if v > 0 else str(-1) for v in executors]) \
                if real_act != 'filterAttentions' else \
             json.dumps([{
                          "userId": executors[0]  # 当前场景下暂只支持一个关注人。
                          }]),
        }

        logger.info('ACTION PARAMS:{}'.format(params))
        return self.Do(params)

    def JudgeStatusExpired(self,status,status_partten):
        expireFlag = -1  # 0：已过期，1：未过期
        expire_partten = ['期']
        for j in expire_partten:
            if j in status:
                for i in status_partten:
                    if i in status:
                        # 未过期
                        expireFlag = 1
                        return expireFlag

                # 已过期
                expireFlag = 0

        return expireFlag

    def SpecifyStatus(self, order, status,*executors):
        statusid = -1
        status_partten = ['未','待','没有','尚未','还没有','没']
        left_status = [i for i in status_partten if i in status]
        statusid = 0 if len(left_status) else 3

        # 判断是否过期
        isExpire = self.JudgeStatusExpired(status,status_partten)

        if isExpire == 1:
            starttime = None
            logger.info('未过期')
            _, _endtime = CNTime('今天').guess_time()
            logger.info('{}'.format(_endtime))
            # endtime = str(int(_endtime.timestamp() * 1000))
            return self.SpecifyTime(order, starttime, _endtime, *executors)
        elif isExpire == 0:
            logger.info('已过期')
            starttime = None
            _, _endtime = CNTime('昨天').guess_time()
            logger.info('{}'.format(_endtime))
            # endtime = str(int(_endtime.timestamp() * 1000))
            return self.SpecifyTime(order, starttime, _endtime, *executors)

        params = {
            'srcInput': order,
            'stateId': statusid,
            'filterAssigners': ','.join([str(v) if v > 0 else str(-1) for v in executors]),
        }

        logger.info('PARAMS:{}'.format(params))
        return self.Do(params)


    def SpecifyExecutors(self, order, *executors):
        params = {
            'srcInput': order,
            'filterAssigners': ','.join([str(v) if v > 0 else str(-1) for v in executors]),
        }
        return self.Do(params)


    def SpecifyFollowers(self, order, *followers):
        params = {
            'srcInput': order,
            'filterAttentions': json.dumps([{"userId": ','.join([str(v) if v > 0 else str(-1) for v in followers])}]),
        }
        return self.Do(params)


    def SpecifyKeywords(self, order, keywords):
        params = {
            'srcInput': order,
            'contentFilter': keywords,
        }
        return self.Do(params)


    def SpecifyKeywordsTime(self, order, keywords, period):
        params = {
            'srcInput': order,
            'contentFilter': keywords,
            'timeType': 1,
        }
        ts, te = period
        if ts:
            params['startTime'] = floor(ts.timestamp()*1000)
        if te:
            params['endTime'] = ceil(te.timestamp()*1000)

        return self.Do(params)



class ApiDocCount(API):
    def __init__(self, agent='', agentuid=''):
        super().__init__(agent, agentuid)

        # doc: http://git.teamin.cc:4999/index.php?s=/4&page_id=116
        self.api = '/v1/weixin/assistant/netdisk/count/ai'


    def Do(self, params={}):
        #params = {
        #    'startTime': '',
        #    'endTime': '',
        #    'filterCreaters': '',
        #    'circleNameFilter': '',
        #    'filter': '',
        #    'srcInput': '',
        #}

        res, _ = self.Get(self.api, params)

        count = res.get('fileCount', 0)

        # if count == 0:
        #     params = {
        #         'srcInput': params['srcInput'],
        #     }

        params['nlp_about'] = res.get('aboutUsers', [])
        params['nlp_keywords'] = res.get('keywords', [])
        return count, web.UrlQueryDoc(params, count, res)


    def All(self, order):
        params = {
            'srcInput': order,
            'filter': order,
        }
        return self.Do(params)


    def Deprecated(self, starttime, endtime, order, keyword):
        params = {
            'srcInput': order,
        }
        if starttime > 0 and endtime > 0:
            params['startTime'] = starttime
            params['endTime'] = endtime
        if keyword:
            params['filter'] = keyword

        return self.Do(params)

    def JudgeStatusExpired(self,status,status_partten):
        expireFlag = -1  # 0：已过期，1：未过期
        expire_partten = ['期']
        for j in expire_partten:
            if j in status:
                for i in status_partten:
                    if i in status:
                        # 未过期
                        expireFlag = 1
                        return expireFlag

                # 已过期
                expireFlag = 0

        return expireFlag

    def SpecifyDblSelect(self, order, *executors, **opr_dict):

        params = {
            'srcInput': order,
        }

        # 1 谁+时间
        if (opr_dict.get('stime',None) != None or opr_dict.get('etime',None) != None) and  opr_dict.get('executors',None) != None:
            if opr_dict.get('stime',None) != None:
                params['startTime'] = floor(opr_dict.get('stime').timestamp() * 1000)
                params['timeType'] = 1
            if opr_dict.get('etime',None) != None:
                params['endTime'] = ceil(opr_dict.get('etime').timestamp() * 1000)
                params['timeType'] = 1

            params['filterCreaters'] = ','.join([str(v) if v > 0 else str(-1) for v in executors])
            logger.info('PARAMS:{}'.format(params))
            return self.Do(params)

        # 2 时间+行为
        if (opr_dict.get('stime', None) != None or opr_dict.get('etime', None) != None) and opr_dict.get('actions',None) != None:
            if opr_dict.get('stime', None) != None:
                params['startTime'] = floor(opr_dict.get('stime').timestamp() * 1000)
                params['timeType'] = 1
            if opr_dict.get('etime', None) != None:
                params['endTime'] = ceil(opr_dict.get('etime').timestamp() * 1000)
                params['timeType'] = 1

            params['filterCreaters'] = ','.join([str(v) if v > 0 else str(-1) for v in executors])
            logger.info('ST&ACT PARAMS:{}'.format(params))
            return self.Do(params)


    def SpecifyKeywordsTime(self, order, keywords, period):
        params = {
            'srcInput': order,
            'filter': keywords,
        }
        ts, te = period
        if ts:
            params['startTime'] = floor(ts.timestamp()*1000)
        if te:
            params['endTime'] = ceil(te.timestamp()*1000)

        return self.Do(params)


    def SpecifyCreators(self, order, *creators):
        params = {
            'srcInput': order,
            'filterCreaters': ','.join([str(v) if v > 0 else str(-1) for v in creators]),
        }
        return self.Do(params)


    def SpecifyKeywords(self, order, keywords):
        params = {
            'srcInput': order,
            'filter': keywords,
        }
        return self.Do(params)


    def SpecifyTime(self, order, starttime, endtime, *creators):
        params = {
            'srcInput': order,
            'filterCreaters': ','.join([str(v) if v > 0 else str(-1) for v in creators]),
            'startTime': starttime,
            'endTime': endtime,
        }

        ts = starttime
        te = endtime
        if ts:
            params['startTime'] = floor(ts.timestamp() * 1000)
        if te:
            params['endTime'] = ceil(te.timestamp() * 1000)
        return self.Do(params)


class ApiBindInfo(API):
    def __init__(self):
        super().__init__()

        # doc: http://git.teamin.cc:4999/index.php?s=/4&page_id=139
        self.api = '/v1/users/bind_info'
        self.key = 'zkfHsKlfHcO9zmm1v8FMuWxsCzH4iE9i'
        self.secret = '54V0h82fuj2FqAC6Tm9mqYkEb1pY95dK'


    def Do(self, params={}):
        #params = {
        #    'type': '',
        #    'value': '',
        #}

        params['key'] = self.key
        params['secret'] = self.secret

        res, _ = self.Get(self.api, params)

        return res


    def TeaminUID(self, agent, agentuid):
        params = {}

        if agent == 'WECHAT':
            params['type'] = 'wxuid'
        elif agent == 'WXOA':
            params['type'] = 'mpopenid'
        params['value'] = agentuid

        try:
            res = self.Do(params)
        except API.Exception as e:
            if e.args[1].status_code == 400:
                return 0

        if res and 'userId' in res:
            return res['userId']
        return 0
