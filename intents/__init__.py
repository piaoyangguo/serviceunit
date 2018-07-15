import logging
logger = logging.getLogger(__name__)

from baidu.bce import BCE
from serviceunit import settings
from edge import Response

from app.unit import parse_intent

from intents.message import IntentMessage
from intents.unknown import IntentUnknown
from intents.upload_file import IntentUploadFile
from intents.upload_file2 import IntentUploadFile2
from intents.help import IntentHelp
from intents.help2 import IntentHelp2
from intents.binding import IntentBinding
from intents.qset_remind import IntentQsetRemind

from intents.remind import IntentRemind
from intents.new_task import IntentNewTask
from intents.create_task import IntentCreateTask
from intents.qtask_exec import IntentQtaskExec
from intents.qtask_fos import IntentQtaskFos
from intents.qtask_naked import IntentQtaskNaked
from intents.qtask_about import IntentQtaskAbout
from intents.qtask_any import IntentQtaskAny
from intents.view_task import IntentViewTask
from intents.qdoc_crt import IntentQdocCrt
from intents.qdoc_about import IntentQdocAbout
from intents.qdoc_naked import IntentQdocNaked
from intents.qdoc_any import IntentQdocAny
from intents.qtask_dbl import IntentQtaskDbl
from intents.qtask_sgl import IntentQtaskSgl
from intents.qdoc_sgl import IntentQdocSgl
from intents.qdoc_dbl import IntentQdocDbl


SceneID = getattr(settings, 'UNIT_SCENE_ID')

def Message(msg):
    return IntentMessage(msg)

def Analyze(request):
    query = request.Message()
    try:
        intent_json = BCE().UNIT(SceneID, query)
        if 'result' not in intent_json:
            logger.info('request baidu failure: {}'.format(str(intent_json)))
            intent_json = {}
    except Exception as e:
        logger.debug('request baidu exception: {}'.format(str(e)))
        intent_json = {}

    if not intent_json:
        return IntentMessage('抱歉，服务走丢了… \n请稍后重试')

    intent = parse_intent(intent_json, SceneID, query, request.UID())

    s = request.Session
    request.Session = None
    _intent = analyze(request, intent)
    resp = _intent.Go()
    if resp.Intent == Response.Intent_UNKNOWN and s:
        request.Session = s
        if s.Intent == Response.Intent_CREATE_TASK:
            return IntentNewTask(request, intent)
        if s.Intent == Response.Intent_QUERY_TASK:
            return IntentQtaskNaked(request, intent)
        if s.Intent == Response.Intent_QUERY_DOC:
            return IntentQdocNaked(request, intent)

    return _intent
            

def analyze(request, intent):
    query = request.Message()
    qu = intent.current_qu_intent
    
    # 指令：上传文档2
    if qu == IntentUploadFile2.NAME:
        return IntentUploadFile2(request, intent)

    # 指令：帮助2
    if qu == IntentHelp2.NAME:
        if '文档' in query or '上传' in query:
            return IntentUploadFile2(request, intent)
        return IntentHelp2(request, intent)

    # 指令：绑定账号
    if qu == IntentBinding.NAME:
        return IntentBinding(request, intent)

    # 指令：上传文档(deprecated)
    if qu == IntentUploadFile.NAME:
        return IntentUploadFile(request, intent)

    # 指令：帮助(deprecated)
    if qu == IntentHelp.NAME:
        return IntentHelp(request, intent)

    # 指令：查询消息提醒的设置
    if qu == IntentQsetRemind.NAME:
        #return IntentQsetRemind(request, intent)
        return IntentHelp2(request, intent)

    # 模板匹配，要求高度匹配
    if intent.intent_confidence < 90:
        return IntentUnknown(request, intent)

    # 指令：创建任务
    if qu == IntentNewTask.NAME:
        return IntentNewTask(request, intent)

    # 指令：提醒
    if qu == IntentRemind.NAME:
        return IntentRemind(request, intent)

    # 指令： 二重条件查询任务
    if qu == IntentQtaskDbl.NAME:
        return IntentQtaskDbl(request, intent)

    # 指令： 查询单一任务
    if qu == IntentQtaskSgl.NAME:
        return IntentQtaskSgl(request, intent)

    # 指令：查询任务执行人
    if qu == IntentQtaskExec.NAME:
        return IntentQtaskExec(request, intent)

    # 指令：查询任务关注人
    if qu == IntentQtaskFos.NAME:
        return IntentQtaskFos(request, intent)

    # 指令：关于条件的任务查询
    if qu == IntentQtaskAbout.NAME:
        return IntentQtaskAbout(request, intent)

    # 指令：裸条件查询任务
    if qu == IntentQtaskNaked.NAME:
        return IntentQtaskNaked(request, intent)

    # 指令：兜底任务查询
    if qu == IntentQtaskAny.NAME:
        return IntentQtaskAny(request, intent)

    # 指令：查询文档上传人
    if qu == IntentQdocCrt.NAME:
        return IntentQdocCrt(request, intent)

    # 指令：二重条件查询文档
    if qu == IntentQdocDbl.NAME:
        return IntentQdocDbl(request, intent)

    # 指令：单一条件查询文档
    if qu == IntentQdocSgl.NAME:
        return IntentQdocSgl(request, intent)

    # 指令：关于条件的文档查询
    if qu == IntentQdocAbout.NAME:
        return IntentQdocAbout(request, intent)

    # 指令：裸条件查询文档
    if qu == IntentQdocNaked.NAME:
        return IntentQdocNaked(request, intent)

    # 指令：兜底文档查询
    if qu == IntentQdocAny.NAME:
        return IntentQdocAny(request, intent)

    task_slot = intent.slots.filter(type='user_task').first()
    if task_slot:
        if qu == IntentCreateTask.NAME:
            if task_slot.original_word in ['文档', '文件']:
                return IntentUploadFile(request, intent)
            return IntentCreateTask(request, intent)

        if qu == IntentViewTask.NAME:
            return IntentViewTask(request, intent)	

    return IntentUnknown(request, intent)
