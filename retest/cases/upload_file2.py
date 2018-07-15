import reg
from polymer import Polymer

IntentName = 'UPLOAD_FILE2'


# <base>

我想   = Polymer(['我想', '我想要', '我要', '我准备', '我希望'])
上传   = Polymer(['上传', '保存', '添加', '创建', '提交', '上载', '新建', '建', '加', '存'])
文档   = Polymer(['文档', '文件', '文本', '档案'])
一份   = Polymer(['一份', '一个', '一些', '几个', '几份', '几份儿', '一份儿', '个', '份'])
怎么   = Polymer(['怎么', '怎样', '如何', '该如何', '我应该怎么', '应该怎么', '应该如何', '我该怎么', '我该如何', '我应该如何', '我如何', '我怎么', '我要怎么', '我要如何'])

啊     = Polymer(['啊', '呀'])

# </base>


reg.AddRules(
    IntentName,
    Polymer(我想.OR(), 上传, 一份.OR(), 文档, 啊.OR()),
    Polymer(怎么, 上传, 一份.OR(), 文档, 啊.OR()),
)
