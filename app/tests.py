import json

from django.test import TestCase, Client

from app.models import Intent


class IntentTest(TestCase):
    def setUp(self):
        self.user_id = '5220414529038490693'

    def test_create(self):
        Intent.objects.create(user_id=self.user_id, query='任务', current_qu_intent='TEST', intent_confidence=100)


class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def post(self, content):
        payload = {'type': 1, 'user_id': '1545446145613545', 'content': content}
        r = self.client.post('/unit/', data=payload)
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content.decode('utf8'), encoding='utf8')
        return result['intent'], result['message']

    def test_new_task(self):
        intent, message = self.post('创建任务，小明下午开会，315会议室带上一棵松')
        self.assertEqual(intent, 1)
        self.assertEqual(message, '小明下午开会，315会议室带上一棵松')

    def test_view_task_1(self):
        intent, message = self.post('搜索任务，最近三天的任务')
        self.assertEqual(intent, 2)
        # self.assertEqual(message, '我最近的任务')

    def test_view_task_2(self):
        intent, message = self.post('查一下我最近的任务')
        self.assertEqual(intent, 2)
        # self.assertEqual(message, '我最近的任务')

    def test_view_task_3(self):
        intent, message = self.post('查看我明天的任务')
        self.assertEqual(intent, 2)
        # self.assertEqual(message, '我明天的任务')

    def test_view_task_4(self):
        intent, message = self.post('查询我的任务')
        self.assertEqual(intent, 2)

    def test_view_file_1(self):
        intent, message = self.post('搜索文档，我最近的上传的文档')
        self.assertEqual(intent, 4)
        # self.assertEqual(message, '我最近的上传的文档')

    def test_view_file_2(self):
        intent, message = self.post('查一下我最近的文档')
        self.assertEqual(intent, 4)
        # self.assertEqual(message, '我最近的文档')

    def test_view_jabber(self):
        intent, message = self.post('天气不错噢')
        self.assertEqual(intent, -1)
