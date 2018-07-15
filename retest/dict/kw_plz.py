from polymer import Polymer

# <base>

你       = Polymer(['你', '您'])
请       = Polymer(['请'])
请你     = Polymer(请, 你.OR())
麻烦     = Polymer(['麻烦', '劳驾'])
麻烦你   = Polymer(麻烦, 你.OR())
请麻烦你 = Polymer(请.OR(), 麻烦, 你.OR())
现在     = Polymer(['现在', '立刻', '马上', '尽快', '立即', '当下'])
帮忙     = Polymer(['帮忙'])
我       = Polymer(['我'])
帮       = Polymer(['帮', '替', '代', '帮助', '协助', '辅助', '替代'])
想要     = Polymer(['要', '想', '想要', '希望', '要求', '需要'])

# </base>

models = [
    请, 

    Polymer(现在.OR(), 请你.OR(), 帮忙),
    Polymer(请你.OR(), 现在.OR(), 帮忙),
    Polymer(请你.OR(), 帮忙, 现在.OR()),
    Polymer(现在.OR(), 请你.OR(), 帮, 我),
    Polymer(请你.OR(), 现在.OR(), 帮, 我),
    Polymer(请你.OR(), 帮, 我, 现在.OR()),

    Polymer(请.OR(), 现在.OR(), 麻烦你.OR(), 帮忙),
    Polymer(请.OR(), 麻烦你.OR(), 现在.OR(), 帮忙),
    Polymer(请.OR(), 麻烦你.OR(), 帮忙, 现在.OR()),
    Polymer(请.OR(), 现在.OR(), 麻烦你.OR(), 帮, 我),
    Polymer(请.OR(), 麻烦你.OR(), 现在.OR(), 帮, 我),
    Polymer(请.OR(), 麻烦你.OR(), 帮, 我, 现在.OR()),

    Polymer(现在.OR(), 请麻烦你.OR(), 帮忙),
    Polymer(请麻烦你.OR(), 现在.OR(), 帮忙),
    Polymer(请麻烦你.OR(), 帮忙, 现在.OR()),
    Polymer(现在.OR(), 请麻烦你.OR(), 帮, 我),
    Polymer(请麻烦你.OR(), 现在.OR(), 帮, 我),
    Polymer(请麻烦你.OR(), 帮, 我, 现在.OR()),

    Polymer(我, 想要),
    Polymer(我, 现在, 想要),
    Polymer(我, 想要, 现在),
]

kw_plz = Polymer(models)

请 = Polymer.ModelsChooser(models, 100)
