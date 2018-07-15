from polymer import Polymer

from dict.user_q import 查询
from dict.kw_de  import 的


# <base>

知道   = Polymer([
    '知道', '了解', '知晓', '晓得', '知悉', '明白', '搞清楚', '弄清楚', '弄明白',
    '知道一下', '告诉我一下', '告诉我', '知道一下',
])

怎么 = Polymer(['怎么', '怎样', '如何', '怎么样'])
消息 = Polymer(['消息', '通知', '消息通知'])
设置 = Polymer(['设置', '设定', '配置'])
发送 = Polymer(['发送', '送达', '知会', '推送', '提醒', '通知'])
方式 = Polymer(['方式', '方法', '形式', '方案', '策略'])
是   = Polymer(['是'])

# </base>


user_qsr_know = Polymer([知道, 查询])
了解 = user_qsr_know

user_qsr_how = Polymer(消息, 是.OR(), 怎么, 发送, 的.OR())
消息怎么发送 = user_qsr_how

user_qsr_way = Polymer(消息, 的.OR(), 发送, 的.OR(), 方式)
消息发送方式 = user_qsr_way

user_qsr_set = Polymer(消息, 的.OR(), 设置)
消息设置 = user_qsr_set
