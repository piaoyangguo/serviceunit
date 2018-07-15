#! /usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys,os,django
__py_dir__ = os.path.split(os.path.realpath(__file__))[0]
__top_dir__ = os.path.dirname(__py_dir__)
sys.path.append(__top_dir__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serviceunit.settings")
django.setup() 

import time, json
from urllib.parse import urlparse, unquote

import edge
from intents import Analyze
from teamin import web

AGENT = 'WXOA'
USERID = 'oXsrqsuW21XksTV2GpKwAy4ku4zE'

# NEW_TASK
Cases_new_task = [
    # {
    #    'agent': AGENT,
    #    'user_id': USERID,
    #    'content': '创建一条任务给刘德华',
    #    'type': '1',
    #    'session': '',
    # },
    # 交互式创建任务，有事件
    '明天早上为刘德华创建一条牛逼的任务，带上老王去开会',
    '为刘德华在明天早上新建一条任务，带上老李去开会',
    '为刘德华创建个明天晚上去洗澡的活动',
    '为刘德华创建一条牛逼的任务，带上我去洗澡',
    '新建一条明天开会的活动，叫上刘德华',
    '来一条吃早饭的任务',
    '为我创建一条喝牛奶的任务',
    '为我创建一条喝牛奶的任务，就明天早上吧',
    '创建一条喝牛奶的任务，在明天早上',
    '新建一个睡觉的事情，带上刘德华',
    '创建一条去打架的任务',
    '创建任务，喝酒去不去',

    # 交互式创建任务，无时间，无人物
    '我要创建任务',

    # 交互式创建任务，有时间，有人物
    '今天晚上为刘德华创建个任务',
    '给刘德华在明天早上创建条任务',
    '为刘德华创建条明天早上完成的任务',
    '为刘德华创建条明天早上的任务',
    '创建一条明天早上完成的任务，刘德华',
    '创建一条明天早上的任务，刘德华',
    '创建一条任务，明天早上，刘德华',
    '创建一条任务，刘德华，明天早上',

    # 交互式创建任务，无时间
    '为刘德华建一条事情',
    '创建一条给刘德华的任务',
    '创建一条任务，刘德华',
    '创建一条执行人是刘德华的任务',

    # 交互式创建任务，无人物
    '明天早上创建一条任务',
    '创建条明天早上完成的任务',
    '创建条明天早上的任务',
    '创建条任务，明天早上做',
    '创建一条截止时间是明天早上的任务',
]

# QTASK_SINGLE
Cases_qtask_single = [

    '查询刘德华的任务',
    '查询昨天的任务',
    '查询最近一段时间的任务',
    '查询5月3号到5号的任务',
    '查询5月3号到5号之间的任务',
    '查询已完成的任务',
    '查询未完成的任务',
    '查询执行的任务',
    '查询创建的任务',
    '查询关心的任务',
    '查询完成的任务',
    '查询标记完成的任务',

]

# QTASK_DB
Cases_qtask_db = [
    '查询刘德华已完成的任务',
    '查询已完成的刘德华的任务',
    '查询刘德华未完成的任务',
    '查询未完成的刘德华的任务',
    '查询刘德华最近一段时间的任务',
    '查询最近刘德华的任务',
    '查询刘德华5月3号到5号的任务',
    '查询5月3号到5号刘德华的任务',
    '查询5月3号到5号的刘德华的任务',
    '查询刘德华5月3号到5号之间的任务',
    '查询5月3号到5号之间刘德华的任务',
    '查询5月3号到5号期间的刘德华的任务',
    '查询需要小明处理的任务',
    '查询小明创建的任务',
    '查询小明关注的任务',
    '查询需要小明关注的任务',
    '查询刘德华关注的任务',
    '查询刘德华的关注任务',
    '查询需要刘德华关注的任务',
    '查询刘德华标记完成的任务',
    '查询昨天已完成的任务',
    '查询昨天未完成的任务',
    '查询已完成的昨天的任务',
    '查询未完成的昨天的任务',
    '查询5月3日到5日的已完成的任务',
    '查询5月3日到6日的未完成的任务',
    '查询已完成的5月3日至6日的任务',
    '查询未完成的5月3日至7日的任务',
    '查询5号和7号之间的已完成的任务',
    '查询5号和8号之间的未完成的任务',
    '查询已完成的5号和8号之间的任务',
    '查询未完成的5号和8号之间的任务',
    '查询昨天处理的任务',
    '查询明天需要处理的任务',
    '查询5号到6号需要处理的任务',
    '查询需要处理的5号到6号的任务',
    '查询5号和5号之间处理的任务',
    '查询5号和6号之间需要执行的任务',
    '查询需要执行的5号和6号之间的任务',
    '查询昨天创建的任务',
    '查询5号至9号创建的任务',
    '查询创建的5号到9号的任务',
    '查询5号和9号之间创建的任务',
    '查询新建的5号到9号的之间的任务',
    '查询昨天关注的任务',
    '查询关注的昨天的任务',
    '查询5号至9号关注的任务',
    '查询关注的5号至9号的任务',
    '查询5号到9号之间关注的任务',
    '查询关注的5号到9号的任务',
    '查询昨天标记完成的任务',
    '查询标记完成的昨天任务',
    '查询标记完成5号至9号的任务',
    '查询5号至9号标记完成的任务',
    '查询标记完成的5号到9号之间的任务',
    '查询5号到9号标记完成的任务',
    '查询执行的已完成的任务',
    '查询执行的未完成的任务',
    '查询已完成的执行的任务',
    '查询未完成的执行的任务',
    '查询创建的已完成的任务',
    '查询创建的未完成的任务',
    '查询已完成的添加的任务',
    '查询未完成的添加的任务',
    '查询关注的已完成的任务',
    '查询关注的未完成的任务',
    '查询已完成的关注的任务',
    '查询未完成的关注的任务',
]

# REMIND
Cases_remind = [
    '今天晚上记得要提醒刘德华来开会',
    '开会，今天晚上提醒刘德华',
    '创建一条提醒，去和大佬吃饭',
    '创建一条提醒去开会',
    '提醒刘德华来开会',
    '开会，提醒刘德华',
    '提醒，开会',
    '跟刘德华说，明天来开会',
    '为刘德华创建一条提醒，来开会',
    '为刘德华搞一条提醒，开会',
    '发一条提醒给刘德华，过来开会',
    '发送给刘德华一条提醒，过来开会',
    '创建条提醒给刘德华，过来开会',
]

# QTASK_ABOUT
Cases_qtask_about = [
    # 人物 + 关键词
    '查询任务，含有张学友与需求分析有关',
    '查询包含刘德华并与需求分析有关的任务',
    '查询任务，包含需求分析有关的刘德华',
    '查询包含需求分析有关的刘德华的任务',
    # 时间段 + 关键词
    '查询包含昨天到今天与需求分析有关的任务',
    '查询任务，包含昨天到今天与需求分析有关的',
    '查询任务，包含昨天与需求分析有关的',
    '查询包含昨天并与需求分析有关的任务',
    '查询包含需求分析有关的昨天到今天的任务',
    '查询任务，包含需求分析有关的昨天到今天的',
    '查询包含需求分析有关的昨天的任务',
    '查询任务，包含需求分析有关的昨天的',
]

# QDOC_ABOUT
Cases_qdoc_about = [
    # 人物 + 关键词
    '查询文档，包含刘德华并与需求分析有关的',
    '查询包含刘德华并与需求分析有关的文档',
    '查询文档，包含需求分析有关的刘德华的',
    '查询包含需求分析有关的刘德华的文档',
    # 时间段 + 关键词
    '查询包含昨天到今天与需求分析有关的文档',
    '查询文档，包含昨天到今天与需求分析有关的',
    '查询文档，包含昨天与需求分析有关的',
    '查询包含昨天并与需求分析有关的文档',
    '查询包含需求分析有关的昨天到今天的文档',
    '查询文档，包含需求分析有关的昨天到今天的',
    '查询包含需求分析有关的昨天的文档',
    '查询文档，包含需求分析有关的昨天的',
]

# QTASK_EXEC
Cases_qtask_exec = [
    '查询刘德华的执行任务',
    '查询刘德华执行的任务',
    '查询交给刘德华的任务',
    '查询交给刘德华执行的任务',
    '查询执行人是刘德华的任务',
    '查询刘德华是执行人的任务',
]

# QTASK_FOS
Cases_qtask_fos = [
    '查询刘德华关注的任务',
    '查询刘德华的关注任务',
    '查询关注人是刘德华的任务',
    '查询刘德华作为关注人的任务',
    '查询在关注人列表中含有刘德华的任务',
    '查询关注人之中有刘德华的任务',
    '查询刘德华在关注人之中的任务',
]

# QTASK_NAKED
Cases_qtask_naked = [
    '查询任务',
]

# QDOC_DB
Cases_qdoc_db = [
    '查询刘德华昨天的文档',
    '查询昨天刘德华的文档',
    '查询刘德华周一到周三的文档',
    '查询周一至周三刘德华的文档',
    '查询刘德华周一至周三之间的文档',
    '查询周一至周三之间刘德华的文档',
    '查询昨天上传的文档',
    '查询上传的昨天的文档',
    '查询周一至周三上传的文档',
    '查询上传的周一至周三的文档',
    '查询周一到周三之间上传的文档',
    '查询上传的周一到周三之间的文档',
]

# QODC_SINGLE
Cases_qdoc_single = [
    '查询刘德华的文档',
    '查询昨天的文档',
    '查询最近一段时间的文档',
    '查询5月3号到5号的文档',
    '查询5月3号到5号之间的文档',
    '查询上传的文档',
]

# QDOC_NAKED
Cases_qdoc_naked = [
    '查询文档',
    '查询上传的文档',
]

# QTASK_ANY
Cases_qtask_any = [
    '查询与刘德华有关的任务',
    '查询任务, 与需求分析有关',
]

# QDOC_ANY
Cases_qdoc_any = [
    '查询与刘德华有关的文档',
    '查询文档, 与需求分析有关',
]

# QDOC_CRT
Cases_qdoc_crt = [
    '查询刘德华的上传文档',
    '查询刘德华上传的文档',
    '查询上传人是刘德华的文档',
    '查询刘德华是上传人的文档',
]

# QSET_REMIND
Cases_qset_remind = [
    '消息设置',
    '我想了解消息设置',
    '消息发送方式',
    '了解消息发送方式',
    '消息怎么发送',
    '了解消息怎么发送',
]

Cases = ['查询我执行的任务']
Cases = ['查询周星驰执行的任务']
Cases = ['查询关于小明的任务']
Cases = ['查询小明执行的任务']
#Cases = ['查询小明关注的任务']
#Cases = ['查询张曼玉关注的任务']
#Cases = ['查询与我有关的任务']

#Cases = Cases_qtask_exec

#Cases = \
#    Cases_qtask_db + \
#    Cases_qtask_single + \
#    Cases_qdoc_db + \
#    Cases_qdoc_single
# 测试用
Case_test = [
    '查询标记完成的任务',
    '查询任务状态为未完成的任务',
    '查询任务状态为已完成的任务',
    '查询刘德华标记完成的任务',
    '查询执行的已完成的任务',
    '查询执行的未完成的任务',
    '查询已完成的执行的任务',
    '查询未完成的执行的任务',
    '查询创建的已完成的任务',
    '查询创建的未完成的任务',
    '查询已完成的添加的任务',
    '查询未完成的添加的任务',
    '查询关注的已完成的任务',
    '查询关注的未完成的任务',
    '查询已完成的关注的任务',
    '查询未完成的关注的任务',
]

Cases = []

Cases = Cases_qtask_db + \
 Cases_qtask_single + \
 Cases_qdoc_db + \
 Cases_qdoc_single
 #Case_test
# Cases = \
#    Cases_new_task + \
#    Cases_remind + \
# \
#    Cases_qtask_exec + \
#    Cases_qtask_fos + \
#    Cases_qtask_about + \
#    Cases_qtask_naked + \
#    Cases_qtask_any + \
# \
#    Cases_qdoc_crt + \
#    Cases_qdoc_any + \
#    Cases_qdoc_about + \
#    Cases_qdoc_naked + \
# \
#    Cases_qset_remind

def main():
    global Cases
    print('---')
    for case in Cases:
        if type(case) == str:
            case = {
                'agent': AGENT,
                'user_id': USERID,
                'content': case,
                'type': '1',
                'session': '',
            }
        _ts = time.time()

        if int(case['type']) == 0:
            req = edge.Request(case['content'])
        else:
            req = edge.Request(case['content'])

        req.InitAgent(case['agent'], case['user_id'])
        req.InitSession(case['session'])

        intent = Analyze(req)
        resp = intent.Go()
        print('识别意图：{}'.format(intent.NAME))
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
        if type(resp.URL) == web.URL:
            ret['unit']['params'] = resp.URL.Params()
            ret['unit']['names'] = resp.URL.Names()
            ret['unit']['nlp'] = resp.URL.NLP()
            ret['unit']['result'] = resp.URL.Result()
            ret['unit']['extra'] = resp.URL.Extra()

        if not ret['eve']:
            ret['intent'] = -1

        data = json.dumps(ret, ensure_ascii=False, sort_keys=True, indent=4)
        print(case['content'])
        if ret['url']:
            print(unquote(urlparse(ret['url']).query))
        if resp.Session:
            _, payload = resp.Session.GetPayload()
            print(payload)
        print(data)
        _te = time.time()
        print('Assumed: {}ms'.format(round((_te - _ts) * 1000)))
        print('---')

if __name__ == '__main__':
    try:
        open('info.log', 'w').close()
        main()
    except KeyboardInterrupt as ki:
        pass
