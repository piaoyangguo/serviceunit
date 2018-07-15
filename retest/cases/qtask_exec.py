import reg
from polymer import Polymer

IntentName = 'QTASK_EXEC'

查询 = Polymer([
    '查询', '搜索', '查看', '查找', '显示', '展示', '呈现', '展现',
    '给出', '列出', '罗列出', '显示出', '呈现出', '展示出', '展现出',
    '看一下', '找一下', '搜一下', '查一下', '列一下',
    '看一看', '找一找', '搜一搜', '查一查',
    '查', '找', '搜', '看',
])
执行人 = Polymer(['刘德华', '张学友'])
的     = Polymer(['的', '得', '地'])
是     = Polymer([
    '是', '就是', '为',
])
任务   = Polymer([
    '任务', '事情', '活动', '目标', '事项',
    '事儿', '活儿',
    '事', '活',
])
交给   = Polymer(['交给', '指派给', '交付给', '让', '让给', '由', '交由'])
执行v  = Polymer([
    '执行', '负责', '做',
])
执行adj = Polymer(['执行'])
执行er = Polymer([
    '执行人', '负责人',
    '执行者', '负责者',
])

# 追加句式
reg.AddRules(
    IntentName,
    Polymer(查询, 执行人, 的, 任务),
    Polymer(查询, 执行人, 的, 执行adj, 任务),
    Polymer(查询, 执行人, 执行v, 的, 任务),
    Polymer(查询, 交给, 执行人, 的, 任务),
    Polymer(查询, 交给, 执行人, 执行v, 的, 任务),
    Polymer(查询, 执行er, 是, 执行人, 的, 任务),
    Polymer(查询, 执行人, 是, 执行er, 的, 任务),
)

# 追加对识别元素的处理, 如果不追加处理，则表示只检查意图
# (执行人, 'per', '==')
# 执行人: 句式中提取得到的执行人成分
# 'per': UNIT服务解析得到的执行人成分对应的key name
# 比较方式
# '==': 执行全值比较;
# 'in-3': 执行子串比较, A in B 或 B in A 均可, 最多允许误差3个字符, 任意空串均返回False, 标准写法 'in-{digit+}', in-0与==等效
# 'in': 类似 'in-3', 但不介意误差
# func (rule_word, unit_word) bool
#reg.AddHandlers(
#    IntentName,
#    (执行人, 'per', '=='),
#    #(执行人, 'per', 'in'),
#    #(执行人, 'per', func),
#)