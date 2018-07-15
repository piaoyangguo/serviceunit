import reg
from polymer import Polymer

from dict.user_qsr import 了解, 消息发送方式, 消息怎么发送, 消息设置

IntentName = 'QSET_REMIND'


reg.AddRules(
    IntentName,
    Polymer(消息设置),
    Polymer(了解, 消息设置),

    Polymer(消息发送方式),
    Polymer(了解, 消息发送方式),

    Polymer(消息怎么发送),
    Polymer(了解, 消息怎么发送),
)
