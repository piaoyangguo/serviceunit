import logging

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

import edge
import teamin
from intents import Analyze, Message

logger = logging.getLogger(__name__)

class IndexView(APIView):
    """
    request { "agent": "WECHAT", "user_id": "1545446145613545", "type": 1, "content": "添加任务，明天三点开会", "session": "" }
    response { "intent": 1, "message": "明天三点开会", "url": "", "session": "" }

    Request 字段说明:
        agent: 代理来源，WECHAT: 微信; WXOA: 微信公众号; 默认是WECHAT
        user_id: 用户 id
        type:    数据类型,  0 语音  1 文字
        content: 用户输入的文字
        session: 上次请求时服务器返回的session，用于问答时记录会话状态

    Response 字段说明:
        intent:  识别的意图, 1 创建任务, 2 查看任务, 3 搜索任务, 4 搜索文档, 5 帮助, 6 提醒, 7 绑定账号
        message: 意图内容
        url:     搜索意图时，返回链接
        session: 问答句式时有值
        session_id: 兼容session
        eve: bool, False表示意图不完整，需要进一步会话取得更多信息
    """
    declared_fields = ['user_id', 'content', 'type']

    def validate(self, data):
        for field in self.declared_fields:
            if field not in data:
                raise ValidationError({field: 'this field is required.'})

    def post(self, request, *args, **kwargs):
        self.validate(request.data)

        if int(request.data['type']) == 0:
            req = edge.Request(request.FILES['file'])
        else:
            req = edge.Request(request.data['content'])

        req.InitAgent(request.data.get('agent', 'WECHAT'), request.data['user_id'])
        req.InitSession(request.data.get('session', ''))

        try:
            intent = Analyze(req)
        except teamin.business.API.Exception as e:
            if e.args[1].status_code == 401:
                intent = Message('服务器故障，正在抢修中...\n请稍后重试')
            elif e.args[1].status_code == 400:
                intent = Message('服务器昏迷中，正在努力抢救...\n请稍后重试')
            else:
                intent = Message('抱歉，服务器可能迷路了...\n请稍后重试')
        except Exception as e:
            logger.debug(e)
            intent = Message('服务器可能私奔到月球了，正在找回中...\n请稍后重试')

        resp = intent.Go()

        logger.debug('###URL:{}'.format(resp.URL))

        ret = {
            'intent': resp.Intent,
            'session': resp.Session.Serialize() if resp.Session else '',
            'message': resp.Message,
            'url': str(resp.URL),
            'gurl': str(resp.GURL),
            'eve': resp.Eve,
            'unit': {
                'intent': resp.UnitIntent,
                'params': {},
                'names': {},
                'nlp': {},
                'result': {},
                'extra': {},
            },
        }
        if type(resp.URL) == teamin.web.URL:
            ret['unit']['params'] = resp.URL.Params()
            ret['unit']['names'] = resp.URL.Names()
            ret['unit']['nlp'] = resp.URL.NLP()
            ret['unit']['result'] = resp.URL.Result()
            ret['unit']['extra'] = resp.URL.Extra()

        if not ret['eve']:
            ret['intent'] = -1

        logger.debug('@@@ response: ' + str(ret))
        return Response(ret)
