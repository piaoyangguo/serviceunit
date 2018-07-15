import reg
from polymer import Polymer
from dict.user_sglq_asw import *
from dict.user_sglq_ts import 起始时间
from dict.user_sglq_te import 截止时间
from dict.user_tsk import 任务
from dict.user_q import 查询
from dict.kw_de import 的
from dict.kw_plz import 请
from dict.kw_zhi import 至
from dict.kw_qj import 期间
from dict.kw_bei import 被


IntentName = 'QTASK_SINGLE'

#【查询】【谁】的【任务】
#【查询】【时间】的【任务】
#【查询】【时间点】【至】【时间点】的任务
#【查询】【时间点】【和】【时间点】【之间】的任务
#【查询】【已完成】的【任务】
#【查询】【未完成】的【任务】
#"【查询】【执行】的【任务】
#【查询】【被】【完成】的【任务】"
#【查询】【创建】的【任务】
#【查询】【关注】的【任务】
#【查询】【完成】的【任务】
#【查询】【标记】【完成】的【任务】


reg.AddRules(
    IntentName,
    Polymer(请.OR(),查询,人物,的,任务),
    Polymer(请.OR(),查询,截止时间,的,任务),
    Polymer(请.OR(),查询,起始时间,至,截止时间,的,任务),
    Polymer(请.OR(),查询,起始时间,至,截止时间,期间,的,任务),
    Polymer(请.OR(),查询,状态,的,任务),
    Polymer(请.OR(),查询,行为,的,任务),
    Polymer(请.OR(),查询,人物,的,任务),
    Polymer(请.OR(),查询,被,行为,的,任务),
)
