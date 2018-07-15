import reg
from polymer import Polymer

IntentName = 'HELP'


reg.AddRules(
    IntentName,
    Polymer([
        '使用帮助', '使用说明', '例句', '帮助', '使用手册', '怎么用', '需要帮助', '我想要帮助',
    ]),
)
