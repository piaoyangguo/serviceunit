from edge import Response
from serviceunit import settings

intro    = getattr(settings, 'UNIT_INTRO_v2')
helpinfo = getattr(settings, 'UNIT_HELP_v2')

class Message():
    @classmethod
    def Response(cls, msg):
        resp = Response(Response.Intent_UNKNOWN, cls.NAME)
        resp.InitMessage(msg)
        return resp

class UploadFile():
    @classmethod
    def Response(cls):
        resp = Response(Response.Intent_UNKNOWN, cls.NAME)
        resp.InitMessage('好的，请将文档直接发送给我')
        return resp

class Unknown():
    @classmethod
    def Response(cls):
        resp = Response(Response.Intent_UNKNOWN, cls.NAME)
        resp.InitMessage(intro['text'], intro['url'], intro['gurl'])
        return resp

class CreateTask():
    @classmethod
    def Response(cls, msg):
        resp = Response(Response.Intent_CREATE_TASK, cls.NAME)
        resp.InitMessage(msg)
        return resp

    @classmethod
    def Message(cls, payload=None):
        msg = '好的，请告诉我需要创建的任务'
        if payload:
            if 't' in payload and 'w' in payload:
                return msg
            if 't' in payload:
                return '好的，请告诉我{}需要处理的事情'.format(payload['t'])
            if 'w' in payload:
                if payload['w'] not in ['你', '我', '他']:
                    return '好的，请告诉我需要给{}创建的任务内容'.format(payload['w'])
        return msg

    @classmethod
    def ResponseNaked(cls, query, uid, payload=None):
        resp = Response(Response.Intent_CREATE_TASK, cls.NAME)
        resp.InitMessage(cls.Message(payload))
        resp.SetSession(query, uid, payload)
        return resp

class QueryTask():
    @classmethod
    def Message(cls, count, finished, expired):
        if count > 0:
            content = [
                '已找到{}条任务'.format(count),
                '其中包含{}条过期任务，{}条已完成任务'.format(expired, finished),
                '',
                '点这里，查看任务详细信息',
            ]
            if finished + expired == 0:
                content.pop(1)
            elif expired == 0:
                if finished == count:
                    content[1] = '{}条任务均已完成'.format(finished)
                else:
                    content[1] = '其中包含{}条已完成任务'.format(finished)
            elif finished == 0:
                if expired == count:
                    content[1] = '{}条任务均已过期'.format(expired)
                else:
                    content[1] = '其中包含{}条过期任务'.format(expired)
        else:
            content = [
                '抱歉，没有找到符合条件的任务',
                # '',
                # '点这里，查看全部任务详细信息',
            ]
        return '\n'.join(content)
        
    @classmethod
    def Response(cls, count, finished, expired, weburl):
        msg = cls.Message(count, finished, expired)
        resp = Response(Response.Intent_QUERY_TASK, cls.NAME)
        # if '抱歉' in msg:
        #     weburl = ''
        resp.InitMessage(msg, weburl)
        return resp

    @classmethod
    def ResponseNaked(cls, query, uid):
        resp = Response(Response.Intent_QUERY_TASK, cls.NAME)
        resp.InitMessage('好的，请告诉我需要查询任务的全部或部分内容')
        resp.SetSession(query, uid)
        return resp

class QueryDoc():
    @classmethod
    def Message(cls, count):
        if count > 0:
            return '已找到{}个文档, 点击链接查看详情'.format(count)
        return '抱歉，没有找到符合条件的文档'

    @classmethod
    def Response(cls, count, weburl):
        msg = cls.Message(count)
        resp = Response(Response.Intent_QUERY_DOC, cls.NAME)
        # if '抱歉' in msg:
        #     weburl = ''
        resp.InitMessage(msg, weburl)
        return resp

    @classmethod
    def ResponseNaked(cls, query, uid):
        resp = Response(Response.Intent_QUERY_DOC, cls.NAME)
        resp.InitMessage('好的，请告诉我需要查询文档的全部或部分内容')
        resp.SetSession(query, uid)
        return resp

class Help():
    @classmethod
    def Response(cls):
        resp = Response(Response.Intent_HELP, 'HELP2')
        resp.InitMessage(helpinfo['text'], helpinfo['url'], helpinfo['gurl'])
        return resp

class Remind():
    @classmethod
    def Response(cls, msg):
        resp = Response(Response.Intent_REMIND, cls.NAME)
        resp.InitMessage(msg)
        return resp

class Binding():
    @classmethod
    def Response(cls, msg):
        resp = Response(Response.Intent_BINDING, cls.NAME)
        resp.InitMessage(msg)
        return resp

class QuerySettingRemind():
    @classmethod
    def Response(cls, msg):
        resp = Response(Response.Intent_QUERY_SETTING_REMIND, cls.NAME)
        resp.InitMessage(msg)
        return resp
