from polymer import Polymer
from dict.sys_time import sys_time
from dict.sys_period import sys_period

前后 = Polymer([
    '前',
    '后',
])

几 = Polymer(
    '几',
)

日期 = Polymer([
    '日', '天',
    '周', '星期', '礼拜',
    '月',
    '年',
])
common = Polymer([
    '最近',
    '近期',
    '最近一段时间',
    '近段时间',
    '这段时间',
    '最近几天',
    '这几',
    '近几天',
    '凌晨',
    '早晨',
    '晨',
    '月底',
    '一早',
    '早上',
    '早',
    '上午',
    '正午',
    '白天',
    '午后',
    '下午',
    '傍晚',
    '晚上',
    '夜晚',
    '午夜',
    '晚间',
    '夜里',
    '夜间',
    '晚',
    '夜',

])

a = Polymer(
    ['前', '后', '前后'],
    [Polymer.Range(0, 101), Polymer.RangeCN(0, 100)],
    Polymer(日期),
)
day = Polymer(['前', '大前', '当', '昨', '今', '明', '后', '大后'], ['天', '日'])
week = Polymer(['上上', '上', '本', '这', '这个', '当', '下', '下下'], ['周', '礼拜'])
month = Polymer(['上上', '上', '上半', '本', '这', '这个', '当', '下', '下半', '下下'], ['月'])
xun = Polymer(['上', '中', '下'], ['旬'])
year = Polymer(['今', '当', '本', '这', '去', '后', '前', '大前', '后', '大后'], ['年'])

models = [
    sys_time,
    sys_period,
    day, week, month, xun, year, common, a,
]

user_t = Polymer(models)
时间段 = Polymer.ModelsChooser(models, 100)
