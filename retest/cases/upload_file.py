import reg
from polymer import Polymer

IntentName = 'UPLOAD_FILE'


reg.AddRules(
    IntentName,
    Polymer([
        '上传文档', '保存文档', '添加文档', '上传一个文档', '保存一个文档', '我要上传一个文档', '我要保存一个文档',
    ]),
)
