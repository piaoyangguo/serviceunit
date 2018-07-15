import reg
from polymer import Polymer
from dict.user_db_ascr import 创建er,二重行为,二重状态
from dict.user_db_te import 二重截止时间
from dict.user_db_ts import 二重起始时间
from dict.user_db_w import 二重任务人
from dict.user_tsk import 任务
from dict.user_q import 查询
from dict.kw_de import 的
from dict.kw_plz import 请
from dict.kw_zhi import 至
from dict.kw_qj import 期间
from dict.kw_bei import 被
from dict.kw_is import 是

IntentName = 'QTASK_DB'

reg.AddRules(
    IntentName,
    #二重任务人+二重状态
    Polymer(查询,二重任务人,二重状态,的,任务),
    Polymer(查询,二重状态,的,二重任务人,的,任务),

    #二重任务人+二重时间
    Polymer(查询,二重任务人,二重截止时间,的,任务),
    Polymer(查询,二重截止时间,二重任务人,的,任务),
    Polymer(查询,二重任务人,二重起始时间,至,二重截止时间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,二重任务人,的,任务),
    Polymer(查询,二重任务人,二重起始时间,至,二重截止时间,期间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,期间,二重任务人,的,任务),

    #二重任务人+二重行为
    Polymer(查询,被,二重任务人,二重行为,的,任务),
    Polymer(查询,二重任务人,二重行为,的,任务),
    Polymer(查询,二重任务人,的,二重行为,任务),
    Polymer(查询,创建er,是,二重任务人,的,任务),
    Polymer(查询,二重任务人,是,创建er,的,任务),

    #二重时间+二重状态
    Polymer(查询,二重截止时间,二重状态,的,任务),
    Polymer(查询,二重状态,二重截止时间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,二重状态,的,任务),
    Polymer(查询,二重状态,的,二重起始时间,至,二重截止时间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,期间,二重状态,的,任务),
    Polymer(查询,二重状态,的,二重起始时间,至,二重截止时间,期间,的,任务),

    #二重时间+二重行为
    Polymer(查询,二重截止时间,二重行为,的,任务),
    Polymer(查询,二重起始时间,被,二重行为,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,被,二重行为,的,任务),
    Polymer(查询,被,二重行为,的,二重起始时间,至,二重截止时间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,期间,二重行为,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,期间,被,二重行为,的,任务),
    Polymer(查询,被,二重行为,的,二重起始时间,至,二重截止时间,期间,的,任务),
    Polymer(查询,二重起始时间,至,二重截止时间,二重行为,的,任务),
    Polymer(查询,二重行为,的,二重起始时间,至,二重截止时间,的,任务),
    Polymer(查询,二重行为,的,二重起始时间,至,二重截止时间,期间,的,任务),
    Polymer(查询,二重行为,的,二重截止时间,的,任务),


    #二重状态+二重行为
    Polymer(查询,二重行为,的,二重状态,的,任务),
    Polymer(查询,二重状态,二重行为,的,任务),

)



