Rules = {}
Handlers = {}

def AddRules(name, *rules):
    global Rules
    if name not in Rules:
        Rules[name] = []
    Rules[name] += list(rules)

def AddHandlers(name, *handlers):
    global Handlers
    if name not in Handlers:
        Handlers[name] = []
    Handlers[name] += list(handlers)



StaticRules = {}
StaticHandlers = {}

def AddStaticRules(name, *rules):
    global StaticRules
    if name not in StaticRules:
        StaticRules[name] = []
    StaticRules[name] += list(rules)

def AddStaticHandlers(name, *handlers):
    global StaticHandlers
    if name not in StaticHandlers:
        StaticHandlers[name] = []
    StaticHandlers[name] += list(handlers)
