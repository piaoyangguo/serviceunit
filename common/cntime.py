# -*- coding: utf-8 -*-

import re, time
from datetime import datetime
from collections import OrderedDict

import common.cn2dig as cn2dig

# year offset
wyear = OrderedDict([
    ('今年', 0), ('当年', 0), ('本年', 0), ('这年', 0),
    ('明年', 1), ('后年', 2), ('大后年', 3),
    ('上年', -1), ('去年', -1), ('前年', -2), ('大前年', -3),
])
# day offset
wmonth2 = OrderedDict([
    ('年初', (1, 3)), ('年中', (4, 8)), ('年末', (9, 12)),
    ('上半年', (1, 6)), ('下半年', (7, 12)),
])
# month offset
wmonth = OrderedDict([
    ('本月', 0), ('这月', 0), ('这个月', 0), ('当月', 0),
    ('下月', 1), ('下个月', 1), ('下下月', 2), ('下下个月', 2),
    ('上月', -1), ('上个月', -1), ('上上月', -2), ('上上个月', -2),
    ('前月', -1),
])
# week offset
wweek = OrderedDict([
    ('本周', 0), ('这周', 0), ('这星期', 0), ('这个周', 0), ('这个星期', 0), ('这礼拜', 0), ('这个礼拜', 0), ('当周', 0),
    ('下周', 1), ('下星期', 1), ('下个星期', 1), ('下礼拜', 1), ('下个礼拜', 1),
    ('下下周', 2), ('下下星期', 2), ('下下个星期', 2), ('下下礼拜', 2), ('下下个礼拜', 2),
    ('上周', -1), ('上星期', -1), ('上个星期', -1), ('上礼拜', -1), ('上个礼拜', -1),
    ('上上周', -2), ('上上星期', -2), ('上上个星期', -2), ('上上礼拜', -2), ('上上个礼拜', -2),
])
# day offset
wday2 = OrderedDict([
    ('上旬', (1, 10)), ('月初', (1, 5)), ('中旬', (11, 20)), ('下旬', (21, 31)), ('月末', (25, 31)), ('月底', (25, 31)),
    ('前半月', (1, 15)), ('后半月', (16, 31)),
    ('上半月', (1, 15)), ('下半月', (16, 31)),
])
# dayoffset
wday = OrderedDict([
    ('今天', 0), ('当天', 0), ('今日', 0), ('当日', 0),
    ('明天', 1), ('后天', 2), ('大后天', 3),
    ('昨天', -1), ('前天', -2), ('大前天', -3),
    ('今', 0), ('明', 1), ('昨', -1),
])
# houroffset
whour = OrderedDict([
    ('凌晨', (0, 4)),
    ('早晨', (5, 8)), ('晨间', (5, 8)), ('早间', (5, 8)), ('清晨', (5, 8)),
    ('晨',   (5, 8)),
    ('一早', (5, 8)), ('一大早', (5, 8)), ('大清早', (5, 8)),
    ('早上', (8, 10)),
    ('早',   (8, 10)),
    ('上午', (9, 11)),
    ('正午', (11, 13)), ('中午', (11, 13)), ('午间', (11, 13)), ('晌午', (11, 13)),

     
    ('白天', (7, 18)), ('日间', (7, 18)),

    ('午后', (12, 14)),
    ('下午', (14, 18)),

    ('傍晚', (18, 20)),
    ('晚上', (20, 22)),
    ('夜晚', (20, 22)),
    ('午夜', (22, 24)),

    ('晚间', (18, 24)),
    ('夜里', (20, 22)),
    ('夜间', (20, 22)),
    ('晚',   (20, 22)),
    ('夜',   (20, 22)),
])

wAll = (wyear, wmonth, wmonth2, wweek, wday, wday2, whour)

def start_with(word, rng):
    for k in rng:
        if word[0:len(k)] == k:
            return k, rng[k]
    return None, -1

def start_in(word, rng):
    for v in rng:
        if word[:len(v)] == v:
            return v
    return None

class TUnit(object):
    def __init__(self, now, unit):
        # 该时间单位是否被覆盖到，即文本中透漏出的时间概念是否有覆盖到本单位
        # 例："两天后"一词暗含今年，今月，今天+2
        # 例："下午"一词仅覆盖了"时"，表示时段概念，但没有精准值
        self.touch = False
        self.word = '' # 匹配到了哪个词
        self.accuracy = -1 # 精准推测的节点值
        self.offset = 0 # 明天=+1, 两小时后=+2
        self.offsetrange = [] # 表达周概念的时候，限定一个较小的日范围
        self.limit_words = set() # 晚上，上旬
        self.weekday = now.tm_wday + 1 # 应用于周概念，当天是周几（1-7，周一-周日）
        self.amorpm = False # 当难以推断上下午的时候，标记为True
        
        self.maybe = {
            'year': now.tm_year,
            'month': now.tm_mon,
            'day': now.tm_mday,
            'hour': now.tm_hour,
            'minute': now.tm_min,
        }.get(unit)

    def Is(self, acc, word=''):
        self.touch = True
        self.accuracy = acc
        self.offset = 0
        self.offsetrange = []
        self.limit_words = set()
        self.word = word

    def Maybe(self, offset=0):
        self.touch = True
        if self.accuracy >= 0:
            return
        self.accuracy = self.maybe
        self.offset = offset

    def Limit(self, word):
        self.touch = True
        self.limit_words.add(word)

class CNTime(object):
    FreezeTime = None
    REF_UNSPECIFIED = 0 # 未指定
    REF_ASSTART     = 1 # 三天之后
    REF_ASEND       = 2 # 三天之前
    REF_NEARBY      = 3 # 三天左右
    REF_INSIDE      = 4 # 这个月内

    def __init__(self, *words):
        self.when_words = ''.join(words).strip()
        self.valid = False
        if self.FreezeTime:
            now = self.FreezeTime
        else:
            now = time.localtime()
        self.Y = TUnit(now, 'year')
        self.m = TUnit(now, 'month')
        self.d = TUnit(now, 'day')
        self.H = TUnit(now, 'hour')
        self.M = TUnit(now, 'minute')

        self.now = datetime.fromtimestamp(time.mktime(now))
        self.reftime = None
        # 当前默认用INSIDE方式处理未指定范围的情况
        self.reftype = self.REF_UNSPECIFIED
        #self.reftype = self.REF_INSIDE

        self.subtimes = []

        if len(self.when_words) == 0:
            return
        
        words = self.period(self.when_words)
        words = self.fromto(words)
        words = self.numtime(words)
        unfeed_words = self.simpletime(words)
        if len(unfeed_words) == 0:
            self.valid = self._valid()
            return

        # 后备手段
        return

    def maybe_this_year(self, offset, word=''):
        self.Y.Maybe(offset)
        if word:
            self.Y.word = word

    def maybe_this_month(self, offset, word=''):
        self.maybe_this_year(0)
        self.m.Maybe(offset)
        if word:
            self.m.word = word

    def maybe_this_day(self, offset, word=''):
        self.maybe_this_month(0)
        self.d.Maybe(offset)
        if word:
            self.d.word = word

    def maybe_this_hour(self, offset, word=''):
        self.maybe_this_day(0)
        self.H.Maybe(offset)
        if word:
            self.H.word = word

    def maybe_this_minute(self, offset, word=''):
        self.maybe_this_hour(0)
        self.M.Maybe(offset)
        if word:
            self.M.word = word

    rew_最近 = '|'.join(['最近', '近', '这'])
    rew_以来 = '|'.join(['以来', '以前', '之前'])
    rec_分 = re.compile(r'^({})(.+?)(分|分钟)({})?$'.format(rew_最近, rew_以来))
    rec_时 = re.compile(r'^({})(.+?)个?(小时|钟头)({})?$'.format(rew_最近, rew_以来))
    rec_日 = re.compile(r'^({})(.+?)个?(天|日)({})?$'.format(rew_最近, rew_以来))
    rec_周 = re.compile(r'^({})(.+?)个?(周|星期|礼拜)({})?$'.format(rew_最近, rew_以来))
    rec_月 = re.compile(r'^({})(.+?)个?(月|月份)({})?$'.format(rew_最近, rew_以来))
    rec_年 = re.compile(r'^({})(.+?)个?(年|年头)({})?$'.format(rew_最近, rew_以来))

    def period(self, word):
        if re.findall(r'^({})([一这](段时间|阵子))?({})?$'.format(self.rew_最近, self.rew_以来), word):
            return '前30天'
        if re.findall(r'^([这近](段时间|阵子))({})?$'.format(self.rew_以来), word):
            return '前30天'
        if word in ['近期']:
            return '前30天'
        if word in ['当前', '现在']:
            return '今天'
        if word in ['过去', '以前', '之前', '曾经']:
            return '0小时前'
        if word in ['未来', '将来', '今后', '以后', '之后']:
            return '0小时后'

        f = self.rec_分.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前3分钟'
            if cn2dig.Parse(x) >= 0:
                return '前{}分钟'.format(x)

        f = self.rec_时.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前3个小时'
            if cn2dig.Parse(x) >= 0:
                return '前{}个小时'.format(x)

        f = self.rec_日.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前7天'
            if cn2dig.Parse(x) >= 0:
                return '前{}天'.format(x)

        f = self.rec_周.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前3周'
            if cn2dig.Parse(x) >= 0:
                return '前{}周'.format(x)

        f = self.rec_月.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前3个月'
            if cn2dig.Parse(x) >= 0:
                return '前{}个月'.format(x)

        f = self.rec_年.findall(word)
        if f:
            x = f[0][1]
            if x == '几':
                return '前3年'
            if cn2dig.Parse(x) >= 0:
                return '前{}年'.format(x)

        return word

    def fromto(self, word):
        def done(tfrom, tto):
            self.subtimes = [
                self.__class__(tfrom),
                self.__class__(tto),
            ]
            return ''
        f = re.findall(r'^(在|从)?(.+)(至|和|到)(.+)(之间|期间)?$', word)
        if f:
            return done(f[0][1], f[0][3])
        f = re.findall(r'^(自|从)?(.+)(开始|始|起)(至|和|到)?(.+)(结束|终止|终|止)$', word)
        if f:
            return done(f[0][1], f[0][4])
        return word

    def numtime(self, word):
        word = word.strip()

        # TODO: 时区并不能被正确处理，搁置处理
        isop = [
            '%a %b %d %H:%M:%S %Y', # ANSI
            '%a %b %d %H:%M:%S %Z %Y', # UnixDate
            '%a %b %d %H:%M:%S %z %Y', # RubyDate
            '%d %b %y %H:%M %Z', # RFC822
            '%d %b %y %H:%M %z', # RFC822Z
            '%A, %d-%b-%y %H:%M:%S %Z', # RFC850
            '%a, %d %b %Y %H:%M:%S %Z', # RFC1123
            '%a, %d %b %Y %H:%M:%S %z', # RFC1123Z
        ]

        for p in isop:
            try:
                x = datetime.strptime(word, p)
                word = x.strftime('%Y-%m-%d %H:%M')
                break
            except Exception as e:
                #print(e)
                pass

        f = re.findall(r'^(\d{4})(\d{2})(\d{2})\s+(\d{2})(\d{2})(\d{2})?$', word) # 20180514 150300
        if f:
            return '{}年{}月{}日{}点{}分'.format(f[0][0], f[0][1], f[0][2], f[0][3], f[0][4])

        f = re.findall(r'^(\d{4})(\d{2})(\d{2})[日|号]?(.*)$', word) # 20180514
        if f:
            return '{}年{}月{}日{}'.format(f[0][0], f[0][1], f[0][2], f[0][3].strip())

        f = re.findall(r'^(\d{4})([-/])(\d{1,2})\2(\d{1,2})[日|号]?(.*)$', word) # 2018-05-14, 2018/05/14, 2018-5-3
        if f:
            return '{}年{}月{}日{}'.format(f[0][0], f[0][2], f[0][3], f[0][4].strip())

        f = re.findall(r'^(\d{4})[-/](\d{1,2})月?(.*)$', word) # 2018-05, 2018/05, 2018-5
        if f:
            return '{}年{}月{}'.format(f[0][0], f[0][1], f[0][2].strip())

        f = re.findall(r'^(\d{2})[-/](\d{2})[日|号](.*)$', word) # 05-14, 05/14
        if f:
            return '{}月{}日{}'.format(f[0][0], f[0][1], f[0][2].strip())

        return word

    def simpletime(self, word):
        oword = word
        def substrip(*subs):
            nonlocal word, oword
            for v in subs:
                if word[-len(v):] == v:
                    if v == '后':
                        x = word[-3:-1]
                        if x[-1:] == '午' and x[-2:-1] not in ['上', '中', '下']:
                            continue
                    oword = word
                    word = word[:-len(v)].rstrip()
                    return True
            return False

        def prestrip(*pres):
            nonlocal word, oword
            for v in pres:
                if word[:len(v)] == v:
                    oword = word
                    word = word[len(v):].rstrip()
                    return True
            return False

        preok = True
        for v in wAll:
            w, _ = start_with(word, v)
            if w:
                preok = False
                break

        if preok and prestrip('前后'):
            self.subtimes = [
                self.__class__('前' + word),
                self.__class__('后' + word),
            ]
            return ''

        yinei = False
        if preok and prestrip('前', '上', '过去', '之前', '先前', '早前'):
            if len(word) < 2:
                return word
            self.reftype = self.REF_ASSTART
            self.reftime = self.now
            word = self.relative_time(-1, word)
        elif preok and prestrip('后', '下', '未来'):
            if len(word) < 2:
                return word
            self.reftype = self.REF_ASEND
            self.reftime = self.now
            word = self.relative_time(1, word)
        else:
            if preok and prestrip('在', '于'):
                if len(word) < 2:
                    return word

            if substrip('左右', '前后', '附近'):
                if len(word) < 2:
                    return word
                # 过去方向猜测
                self.reftype = self.REF_NEARBY
                word = self.relative_time(-1, word)
            elif substrip('之前', '以前', '前'):
                if len(word) < 2:
                    return word
                self.reftype = self.REF_ASEND
                word = self.relative_time(-1, word)
            elif substrip('之后', '以后', '后'):
                if len(word) < 2:
                    return word
                self.reftype = self.REF_ASSTART
                word = self.relative_time(1, word)
            elif substrip('之内', '以内', '内'):
                if len(word) < 2:
                    return word
                # 过去方向猜测
                yinei = True
                self.reftype = self.REF_ASSTART
                self.reftime = self.now
                word = self.relative_time(-1, word)

        if len(word) == 0:
            return word

        # 指明一个绝对时间以内的说法
        if yinei:
            self.reftype = self.REF_INSIDE
            self.reftime = None

        word_Y = word.strip()
        word_m = self.start_with_year(word_Y).strip()
        word_d = self.start_with_month(word_m).strip()

        word_H = self.start_with_week(word_d).strip()
        if word_H == word_d:
            word_H = self.start_with_day(word_d).strip()

        word_M = self.start_with_hour(word_H).strip()
        word_S = self.start_with_minute(word_M).strip()
        word_end = self.start_with_second(word_S).strip()

        return word_end

    def relative_time(self, actor, word):
        个 = '' if self.reftype == self.REF_UNSPECIFIED else '?'
        f = re.findall(r'^(.+)年(半)?$', word)
        if len(f) > 0:
            if f[0][0] == '半' and f[0][1] == '':
                self.maybe_this_month(6 * actor, word)
                return ''
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                x = 12 * x
                if len(f[0][1]) > 0:
                    x += 6
                self.maybe_this_month(x * actor, word)
                return ''

        f = re.findall(r'^(.+)个{}(半)?月$'.format(个), word)
        if len(f) > 0:
            if f[0][0] == '半' and f[0][1] == '':
                self.maybe_this_day(15 * actor, word)
                return ''
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                x = 30 * x
                if len(f[0][1]) > 0:
                    x += 15
                self.maybe_this_day(x * actor, word)
                return ''
        if word == '半月':
            self.maybe_this_day(15 * actor, word)
            return ''

        f = re.findall(r'^(.+)个(半)?(星期|礼拜)(半)?$', word)
        if len(f) > 0:
            if f[0][0] == '半' and f[0][1] == '' and f[0][3] == '':
                self.maybe_this_day(3 * actor, word)
                return ''
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                x = 7 * x
                if len(f[0][1]) + len(f[0][3]) > 0:
                    x += 3
                self.maybe_this_day(x * actor, word)
                return ''

        f = re.findall(r'^(.+)(周|星期|礼拜)(半)?$', word)
        if len(f) > 0:
            if f[0][0] == '半' and f[0][2] == '':
                self.maybe_this_day(3 * actor, word)
                return ''
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                x = 7 * x
                if len(f[0][2]) > 0:
                    x += 3
                self.maybe_this_day(x * actor, word)
                return ''

        f = re.findall(r'^(.+)(天|日)(半)?$', word)
        if len(f) > 0:
            if f[0][0] == '半' and f[0][2] == '':
                if actor > 0:
                    if self.H.maybe > 15:
                        self.maybe_this_day(1)
                        self.H.Is(14, word)
                    else:
                        self.maybe_this_day(0)
                        self.H.Is(19, word)
                else:
                    if self.H.maybe > 15:
                        self.maybe_this_day(0)
                        self.H.Is(10, word)
                    else:
                        self.maybe_this_day(-1)
                        self.H.Is(14, word)
                return ''
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                if len(f[0][2]) > 0:
                    x += 1
                self.maybe_this_day(x * actor, word)
                return ''

        f = re.findall(r'^(.+)个(半)?(小时|钟头)(半)?$', word)
        if not f:
            f = re.findall(r'^(.+)(小时|钟头)(半)?$', word)
        if f:
            h = f[0][0]
            if len(f[0]) == 4:
                m = len(f[0][1]) + len(f[0][3])
            else:
                m = len(f[0][2])
            if h == '半' and m == 0:
                self.maybe_this_minute(30 * actor, word)
                return ''
            try:
                x = int(float(h) * 60)
            except:
                x = cn2dig.Parse(h) * 60
            if x >= 0:
                if m > 0:
                    x += 30
                self.maybe_this_minute(x * actor, word)
                return ''

        f = re.findall(r'^(.+)(分钟|分)$', word)
        if len(f) > 0:
            x = cn2dig.Parse(f[0][0])
            if x >= 0:
                self.maybe_this_minute(x * actor, word)
                return ''

        f = re.findall(r'^(.+)小时(.+)分钟$', word)
        if len(f) > 0:
            h = f[0][0]
            m = f[0][1]
            if h[-1] == '个':
                h = h[:-1]
            h = cn2dig.Parse(h) * 60
            m = cn2dig.Parse(m)
            if h >= 0 and m >= 0:
                self.maybe_this_minute((h+m) * actor, word)
                return ''

        return word

    def start_with_year(self, word):
        if len(word) == 0:
            return word

        f = word.find('年')
        if f > 0:
            g = cn2dig.Parse(word[:f])
            if g >= 0:
                self.Y.Is(g, word[:f+1])
                word = word[f+1:]
        if not self.Y.touch:
            Y, ot = start_with(word, wyear)
            if Y != None:
                self.maybe_this_year(ot, Y)
                word = word[len(Y):]

        if len(word) == 0:
            return word

        def limit_a():
            s = start_in(word, ['上半年', '前半年'])
            if s != None:
                return '上半年', len(s)
            s = start_in(word, ['下半年', '后半年'])
            if s != None:
                return '下半年', len(s)
            s = start_in(word, ['年初',  '年头'])
            if s != None:
                return '年初', len(s)
            s = start_in(word, ['年中'])
            if s != None:
                return '年中', len(s)
            s = start_in(word, ['年末', '年尾', '年终'])
            if s != None:
                return '年末', len(s)
            return '', 0

        def limit_b():
            s = start_in(word, ['初'])
            if s != None:
                return '年初', len(s)
            s = start_in(word, ['中'])
            if s != None:
                return '年中', len(s)
            s = start_in(word, ['终', '末'])
            if s != None:
                return '年末', len(s)
            return '', 0

        l, l2 = limit_a()
        if len(l) > 0:
            if not self.Y.touch:
                self.maybe_this_year(0)
            word = word[l2:]
            self.m.Limit(l)
        elif self.Y.touch:
            l, l2 = limit_b()
            if len(l) > 0:
                word = word[l2:]
                self.m.Limit(l)

        return word

    def start_with_month(self, word):
        if len(word) == 0:
            return word

        f = word.find('月')
        if f > 0:
            g = cn2dig.Parse(word[:f])
            if g >= 0:
                self.maybe_this_year(0)
                self.m.Is(g, word[:f+1])
                word = word[f+1:]
        if not self.m.touch:
            m, ot = start_with(word, wmonth)
            if m != None:
                self.maybe_this_month(ot, m)
                word = word[len(m):]

        if len(word) == 0:
            return word

        def limit_a():
            s = start_in(word, ['前半月', '上半月', '前半个月', '上半个月'])
            if s != None:
                return '上半月', len(s)
            s = start_in(word, ['后半月', '下半月', '后半个月', '下半个月'])
            if s != None:
                return '下半月', len(s)
            s = start_in(word, ['上旬'])
            if s != None:
                return '上旬', len(s)
            s = start_in(word, ['月初', '月首', '月头'])
            if s != None:
                return '月初', len(s)
            s = start_in(word, ['中旬', '月中'])
            if s != None:
                return '中旬', len(s)
            s = start_in(word, ['下旬'])
            if s != None:
                return '下旬', len(s)
            s = start_in(word, ['月末', '月底', '月尾'])
            if s != None:
                return '月末', len(s)
            return '', 0

        def limit_b():
            s = start_in(word, ['初', '首', '头'])
            if s != None:
                return '月初', len(s)
            s = start_in(word, ['中'])
            if s != None:
                return '中旬', len(s)
            s = start_in(word, ['末', '底', '尾', '末尾'])
            if s != None:
                return '月末', len(s)
            return '', 0

        l, l2 = limit_a()
        if len(l) > 0:
            if not self.m.touch:
                self.maybe_this_month(0)
            word = word[l2:]
            self.d.Limit(l)
        elif self.m.touch:
            l, l2 = limit_b()
            if len(l) > 0:
                word = word[l2:]
                self.d.Limit(l)

        return word

    def start_with_week(self, word):
        if len(word) == 0:
            return word

        offset = 1 - self.d.weekday # 本周周一的相对偏移

        w, ot = start_with(word, wweek)
        if w != None:
            offset = (1 - self.d.weekday) + 7 * ot # 指定周的周一相对偏移
            word = word[len(w):]

        if len(word) == 0:
            self.maybe_this_day(0, w)
            self.d.offsetrange = [offset, offset+6] # 指定周的周一到周日
            return word

        if w != None and len(word) > 0:
            if word[0] in ['末', '天', '日'] or cn2dig.Parse(word[0]) >= 0:
                word = '周' + word

        if word[:3] in ['上半周', '下半周', '前半周', '后半周']:
            self.maybe_this_day(0)
            if word[:1] in ['上', '前']:
                self.d.offsetrange = [offset, offset+2] # 指定周的周一到周三
            else:
                self.d.offsetrange = [offset+3, offset+6] # 指定周的周四到周日
            return word[3:]

        f = re.findall(r'^(星期|礼拜|周)(.)', word)
        if len(f) == 0:
            return word

        if f[0][1] in ['末']:
            self.maybe_this_day(0)
            self.d.offsetrange = [offset+5, offset+6] # 指定周的周六到周日
            return word[len(f[0][0])+1:]

        if f[0][1] in ['天', '日']:
            g = 7
        else:
            g = cn2dig.Parse(f[0][1])
        if g >= 1 and g <= 7:
            self.maybe_this_day(offset + g - 1)
            return word[len(f[0][0])+1:]

        return word

    def start_with_day(self, word):
        if len(word) == 0:
            return word

        f = word.find('日')
        if f < 0:
            f = word.find('号')

        if f > 0:
            g = cn2dig.Parse(word[:f])
            if g >= 0:
                self.maybe_this_month(0)
                self.d.Is(g, word[:f+1])
                word = word[f+1:]

        if self.m.touch and word:
            g = cn2dig.Parse(word)
            if g >= 0:
                self.maybe_this_month(0)
                self.d.Is(g)
                return ''
        else:
            d, ot = start_with(word, wday)
            if d != None:
                self.maybe_this_day(ot, d)
                word = word[len(d):]

        return word

    def start_with_hour(self, word):
        if len(word) == 0:
            return word

        H, ot = start_with(word, whour) # ot 为建议的猜测小时范围
        if H != None:
            self.maybe_this_day(0)
            self.H.Limit(H)
            word = word[len(H):]
            if len(word) == 0:
                return word

        if ot != -1 and (ot[1] - ot[0] < 5):
            ot = (ot[0] + ot[1])/2

        of = 2
        f = word.find('小时')
        if f < 0:
            f = word.find('点钟')
        if f < 0:
            of = 1
        if f < 0:
            f = word.find('时')
        if f < 0:
            f = word.find('点')
        if f < 0:
            f = word.find(':')
        if f < 0:
            f = word.find('：')

        if f > 0:
            ff = re.findall(r'([ap]\.?m\.?)$', word.lower())
            if ff:
                if ff[0][0] == 'a':
                    H, ot = '上午', 10
                else:
                    H, ot = '下午', 15
                self.maybe_this_day(0)
                self.H.Limit(H)
                word = word[:-len(ff[0])]

            g = cn2dig.Parse(word[:f])
            if g >= 0:
                if g <= 12:
                    if H != None: # 存在推断词
                        if ot >= 20:
                            if g <= 5: # 今晚5点，指明天凌晨5点
                                self.d.offset += 1
                            else:
                                g += 12 # 今晚6点，判定指18点
                        elif ot >= 12: # 指明中午/下午
                            if H == '中午' and g > 10: # 中午11点，自然是指上午11点
                                pass
                            else:
                                g += 12
                        else: # 指明早上
                            pass
                    else:
                        if not (f > 1 and word[0] == '0'):
                            self.H.amorpm = True
                self.maybe_this_day(0)
                self.H.Is(g, word[:f+of])
                word = word[f+of:]

        return word

    def start_with_minute(self, word):
        if len(word) == 0 or not self.H.touch:
            return word

        f = re.findall(r'^([^分:：]+)(:|：|分|分钟)', word)
        if len(f) > 0:
            g = cn2dig.Parse(f[0][0])
            if g >= 0:
                self.maybe_this_hour(0)
                self.M.Is(g)
                word = word[len(f[0][0]) + len(f[0][1]):]
            return word

        if word == '半':
            self.M.Is(30)
            return ''
        f = re.findall(r'^(.+)刻$', word)
        if f:
            g = cn2dig.Parse(f[0])
            if g >= 1 and g <= 3:
                self.M.Is(g * 15)
                return ''
        g = cn2dig.Parse(word)
        if g >= 0 and g <= 59:
            self.M.Is(g)
            return ''
        return word

    def start_with_second(self, word):
        if len(word) == 0 or not self.M.touch:
            return word

        f = re.findall(r'^([^秒]+)(秒|秒钟)', word)
        if len(f) > 0:
            g = cn2dig.Parse(f[0][0])
            if g >= 0:
                word = word[len(f[0][0]) + len(f[0][1]):]
            return word

        if word == '半':
            return ''
        g = cn2dig.Parse(word)
        if g >= 0 and g <= 59:
            return ''
        return word

    def _valid(self):
        Y = self.Y.accuracy
        m = self.m.accuracy
        d = self.d.accuracy
        H = self.H.accuracy
        M = self.M.accuracy

        if H == 24:
            H = 0

        try:
            if M >= 0:
                datetime(Y, m, d, H, M)
            elif H >= 0:
                if H == 24:
                    H = 0
                datetime(Y, m, d, H)
            elif d >= 0:
                datetime(Y, m, d)
            elif m >= 0:
                datetime(Y, m, 1)
            else:
                datetime(Y, 1, 1)
            return True
        except:
            return False

    def cal_offset(self):
        if not self.valid:
            return None

        Y = self.Y.accuracy
        Y_ot = self.Y.offset
        m = self.m.accuracy
        m_ot = self.m.offset
        d = self.d.accuracy
        d_ot = self.d.offset
        H = self.H.accuracy
        H_ot = self.H.offset
        M = self.M.accuracy
        M_ot = self.M.offset

        if self.M.touch and M >= 0:
            Mo = M + M_ot
            M = Mo % 60
            H_ot += int(Mo / 60) - (1 if Mo < 0 else 0)
        if self.H.touch and H >= 0:
            Ho = H + H_ot
            H = Ho % 24
            d_ot += int(Ho / 24) - (1 if Ho < 0 else 0)

        def Ymd(Y, m, d, d_ot):
            _t = datetime.fromtimestamp(datetime(Y, m, d).timestamp() + d_ot * 24 * 3600)
            d = _t.day
            ot = (_t.year - Y) * 12 + (_t.month - m)
            return d, ot

        def Ym(m2_ot):
            m2 = m
            Y2 = Y
            Y2_ot = Y_ot
            if self.m.touch and m2 >= 0:
                mo = (m2-1)+m2_ot
                m2 = mo % 12 + 1
                Y2_ot += int(mo / 12) - (1 if mo < 0 else 0)
            if self.Y.touch and Y2 >= 0:
                Y2 = Y2 + Y2_ot
            return Y2, m2

        if self.d.touch and d >= 0:
            #d, ot = Ymd(Y, m, d, d_ot)
            #m_ot += ot
            if len(self.d.offsetrange) == 0:
                d, ot = Ymd(Y, m, d, d_ot)
                m_ot += ot
            else:
                res = []

                d2, ot = Ymd(Y, m, d, 0)
                x0 = Ym(m_ot+ot)
                res.append([x0[0], x0[1], d2, H, M])

                d2, ot = Ymd(Y, m, d, self.d.offsetrange[0])
                x1 = Ym(m_ot+ot)
                res.append([x1[0], x1[1], d2, H, M])

                d2, ot = Ymd(Y, m, d, self.d.offsetrange[1])
                x2 = Ym(m_ot+ot)
                res.append([x2[0], x2[1], d2, H, M])
                return res

        x = Ym(m_ot)
        return [[x[0], x[1], d, H, M]]

    def desc_time(self):
        if self.subtimes:
            if len(self.subtimes) == 1:
                return self.subtimes[0].desc_time()
            return '{} + {}'.format(
                self.subtimes[0].desc_time(),
                self.subtimes[1].desc_time(),
            )

        word = self._desc_time()
        if not word:
            return word
        if self.reftype == self.REF_ASSTART:
            if self.reftime:
                return '{} - {}'.format(word, self.reftime)
            return '{} - +inf'.format(word)
        if self.reftype == self.REF_ASEND:
            if self.reftime:
                return '{} - {}'.format(self.reftime, word)
            return '-inf - {}'.format(word)
        if self.reftype == self.REF_NEARBY:
            return '{} 附近'.format(word)
        if self.reftype == self.REF_INSIDE:
            return '{} 之内'.format(word)
        return word

    def _desc_time(self):
        x = self.cal_offset()
        if x == None:
            return ''
        Y, m, d, H, M = x[0]

        #print(self.Y.__dict__)
        #print(self.m.__dict__)
        #print(self.d.__dict__)
        #print(self.H.__dict__)
        #print(self.M.__dict__)

        if self.M.touch:
            mb = datetime(Y, m, d, H, M)
            if self.H.amorpm:
                return mb.strftime("%Y-%m-%d %H:%M (am?)")
            else:
                return mb.strftime("%Y-%m-%d %H:%M")
        if self.H.touch:
            if H < 0:
                mb = datetime(Y, m, d)
                return mb.strftime("%Y-%m-%d ") + ', '.join(self.H.limit_words)
            else:
                mb = datetime(Y, m, d, H)
                if self.H.amorpm:
                    return mb.strftime("%Y-%m-%d %H (am?)")
                return mb.strftime("%Y-%m-%d %H")
        if self.d.touch:
            if len(self.d.offsetrange) > 0:
                mb1 = datetime(x[1][0], x[1][1], x[1][2])
                mb2 = datetime(x[2][0], x[2][1], x[2][2])
                return mb1.strftime("%Y-%m-%d") + " ~ " + mb2.strftime("%Y-%m-%d")
            elif d < 0:
                mb = datetime(Y, m, 1)
                return mb.strftime("%Y-%m ") + ', '.join(self.d.limit_words)
            else:
                mb = datetime(Y, m, d)
                return mb.strftime("%Y-%m-%d")
        if self.m.touch:
            if m < 0:
                mb = datetime(Y, 1, 1)
                return mb.strftime("%Y ") + ', '.join(self.m.limit_words)
            else:
                mb = datetime(Y, m, 1)
                return mb.strftime("%Y-%m")
        if self.Y.touch:
            mb = datetime(Y, 1, 1)
            return mb.strftime("%Y")

        return ''

    @classmethod
    def datetime(cls, origin, offset):
        origin = datetime(*origin).timestamp()
        return datetime.fromtimestamp(origin + offset)

    def guess_time(self):
        if self.subtimes:
            if len(self.subtimes) == 1:
                return self.subtimes[0].guess_time()
            return self.Merge(
                self.subtimes[0].guess_time(),
                self.subtimes[1].guess_time(),
            )

        x = self.cal_offset()
        if x == None:
            return None, None
        Y, m, d, H, M = x[0]

        def guess_ampm(H):
            if self.H.amorpm:
                #if Y == self.Y.maybe and m == self.m.maybe and d == self.d.maybe: # 当日
                #     猜测过去时
                #    if self.H.maybe >= H:
                #        if H == 0:
                #            return 24
                #        return H + 12
                #    return H
                # 常识推理
                if H >= 1 and H <= 6: # 1点-6点默认为下午，7点-11点默认为上午
                    return H + 12
            return H

        def day_overflow(H):
            a, b, c = self.d.offset, self.H.accuracy, self.H.offset
            self.d.offset, self.H.accuracy, self.H.offset = a+1, H%24, 0
            x = self.guess_time()
            self.d.offset, self.H.accuracy, self.H.offset = a, b, c
            return x

        ots, ote = 0, 0

        if self.M.touch:
            H = guess_ampm(H)
            if H >= 24:
                return day_overflow(H)
            start = datetime(Y, m, d, H, M, 0)
            end   = datetime(Y, m, d, H, M, 59)
            if self.reftype == self.REF_ASSTART:
                return start, self.reftime
            if self.reftype == self.REF_ASEND:
                return self.reftime, start
            if self.reftype == self.REF_INSIDE or \
               self.reftype == self.REF_UNSPECIFIED:
                return start, end
            if self.reftype == self.REF_NEARBY: # 前后1m
                start2 = datetime.fromtimestamp(start.timestamp() - 1*60)
                end2   = datetime.fromtimestamp(start.timestamp() + 2*60-1)
                return start2, end2
        if self.H.touch:
            if H < 0:
                H = 0
                ots, ote = whour[list(self.H.limit_words)[0]]
            else:
                H = guess_ampm(H)
                if H >= 24:
                    return day_overflow(H)
            start = self.datetime((Y, m, d, H, 0, 0), ots*3600)
            end   = self.datetime((Y, m, d, H, 59, 59), ote*3600)
            if self.reftype == self.REF_ASSTART:
                return start, self.reftime
            if self.reftype == self.REF_ASEND:
                return self.reftime, start
            if self.reftype == self.REF_INSIDE or \
               self.reftype == self.REF_UNSPECIFIED:
                return start, end
            if self.reftype == self.REF_NEARBY: # 前后1h
                start2 = datetime.fromtimestamp(start.timestamp() - 1*3600)
                end2   = datetime.fromtimestamp(start.timestamp() + 2*3600-1)
                return start2, end2
        if self.d.touch:
            if len(self.d.offsetrange) > 0: # 限定天级别的范围，一般为周限定
                ots, ote = self.d.offsetrange[0], self.d.offsetrange[1]
            elif d < 0:
                d, ote = wday2[list(self.d.limit_words)[0]]
                while True:
                    try:
                        datetime(Y, m, ote)
                        break
                    except Exception:
                        ote -= 1
                ote -= d

            start = self.datetime((Y, m, d, 0, 0, 0), ots*86400)
            end   = self.datetime((Y, m, d, 23, 59, 59), ote*86400)
            if self.reftype == self.REF_ASSTART:
                return start, self.reftime
            if self.reftype == self.REF_ASEND:
                return self.reftime, start
            if self.reftype == self.REF_INSIDE or \
               self.reftype == self.REF_UNSPECIFIED:
                return start, end
            if self.reftype == self.REF_NEARBY: # 前后1d
                start2 = datetime.fromtimestamp(start.timestamp() - 1*24*3600)
                end2   = datetime.fromtimestamp(start.timestamp() + 2*24*3600-1)
                return start2, end2
        if self.m.touch:
            if m < 0:
                ms, me = wmonth2[list(self.m.limit_words)[0]]
            else:
                ms, me = m, m
            start = datetime(Y, ms, 1, 0, 0, 0)
            if me == 12:
                end = self.datetime((Y+1, 1, 1, 0, 0, 0), -1)
            else:
                end = self.datetime((Y, me+1, 1, 0, 0, 0), -1)
            if self.reftype == self.REF_ASSTART:
                return start, self.reftime
            if self.reftype == self.REF_ASEND:
                return self.reftime, start
            if self.reftype == self.REF_INSIDE or \
               self.reftype == self.REF_UNSPECIFIED:
                return start, end
            if self.reftype == self.REF_NEARBY: # 前后10d
                start2 = datetime.fromtimestamp(start.timestamp() - 10*24*3600)
                end2   = datetime.fromtimestamp(start.timestamp() + 11*24*3600-1)
                return start2, end2
        if self.Y.touch:
            start = datetime(Y, 1, 1, 0, 0, 0)
            end   = datetime(Y, 12, 31, 23, 59, 59)
            if self.reftype == self.REF_ASSTART:
                return start, self.reftime
            if self.reftype == self.REF_ASEND:
                return self.reftime, start
            if self.reftype == self.REF_INSIDE or \
               self.reftype == self.REF_UNSPECIFIED:
                return start, end
            if self.reftype == self.REF_NEARBY: # 前后30d
                start2 = datetime.fromtimestamp(start.timestamp() - 30*24*3600)
                end2   = datetime.fromtimestamp(start.timestamp() + 31*24*3600-1)
                return start2, end2
        return None, None

    @classmethod
    def Merge(cls, tfrom, tto):
        tfrom1, tto1 = tfrom
        tfrom2, tto2 = tto
        # tfrom和tto在逻辑上是可能无法形成常规理解上的连续时段
        # 采取的策略则是取: tfrom1-tto2
        if tfrom1 and tto2:
            if tfrom1.timestamp() < tto2.timestamp():
                return tfrom1, tto2
            return None, None
        return tfrom1, tto2
