import sys,os,django
__py_dir__ = os.path.split(os.path.realpath(__file__))[0]
__top_dir__ = os.path.dirname(__py_dir__)
sys.path.append(__top_dir__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "serviceunit.settings")
django.setup() 

import edge
from intents import Analyze

def Do(agent, userid, sentence):
    req = edge.Request(sentence)

    req.InitAgent(agent, userid)
    req.InitSession('')

    return Analyze(req)
