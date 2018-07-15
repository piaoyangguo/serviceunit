import logging
from datetime import timedelta

import requests
from django.db import models
from django.utils import timezone

from app.matcher import to_date

logger = logging.getLogger()


class Intent(models.Model):
    #agent = models.CharField(max_length=32, verbose_name='代理来源', default='WECHAT')
    user_id = models.CharField(max_length=32, verbose_name='用户ID')
    query = models.CharField(max_length=255, verbose_name='输入语句')

    current_qu_intent = models.CharField(max_length=20, verbose_name='当前意图')
    intent_confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='意图置信度')

    interval = models.CharField(max_length=40, blank=True, verbose_name='时间段')
    url = models.TextField(blank=True, verbose_name='查询的url')

    def set_interval(self, start_time, end_time, url):
        if start_time and end_time:
            self.interval = to_date(start_time) + '-' + to_date(end_time)
        self.url = url
        self.save()

    class Meta:
        verbose_name = '解析的意图'
        verbose_name_plural = '解析的意图'


class Action(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='actions', verbose_name='关联意图')

    main_exe = models.CharField(max_length=20, verbose_name='执行函数')
    say = models.CharField(max_length=20, verbose_name='返回对话')
    confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='置信度')
    action_id = models.CharField(max_length=100, verbose_name='动作名称,fail_action未命中任何意图')

    """
    act_type	动作类型，clarify|satisfy|guide 澄清|满足|引导
    faqguide： faq引导
    act_target	动作的目标，intent|slot|slot_type
    act_target_detail	动作目标详细内容
    action_type_detail	动作类型的详细内容
    """
    action_type = models.TextField(verbose_name='动作类型')
    arg_list = models.TextField(verbose_name='动作参数',
                                help_text='只当action是做意图或词槽澄清的时候,这里才会赋值;"string"通常是意图or词槽名称')
    hint_list = models.TextField(verbose_name='动作引导选项',
                                 help_text='如果当前动作有引导或faq问答中存在多个question需要进一步澄清,则该域存在')


class BotMergedSlot(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='slots', verbose_name='关联意图')

    confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='词槽置信度')
    original_word = models.CharField(max_length=100, verbose_name='原始词槽值')
    normalized_word = models.CharField(max_length=100, verbose_name='词槽归一后的值')
    length = models.IntegerField(default=0, verbose_name='字节总量')
    offset = models.IntegerField(default=0, verbose_name='字节偏移值')
    type = models.CharField(max_length=100, verbose_name='词槽类型')

    class Meta:
        ordering = ['-confidence', ]
        verbose_name = '词槽列表'
        verbose_name_plural = '词槽列表'


class IntentCandidate(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='candidates', verbose_name='关联意图')

    intent_candidate = models.CharField(max_length=100, verbose_name='候选意图')
    intent_confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='意图置信度')

    slots = models.TextField(verbose_name='词槽列表')

    intent_need_clarify = models.BooleanField(verbose_name='意图是否需要澄清')

    from_who = models.CharField(max_length=100, verbose_name='哪个qu出的结果')
    match_info = models.CharField(max_length=256, verbose_name='匹配信息,比如匹配了哪个模板')

    class Meta:
        verbose_name = '意图候选项'
        verbose_name_plural = '意图候选项'


class LexicalAnalysis(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='lexicons', verbose_name='关联意图')

    basic_word = models.TextField(verbose_name='当前term的基础粒度分词')
    type = models.CharField(max_length=100, verbose_name='NER类型')
    term = models.CharField(max_length=100, verbose_name='当前term')
    weight = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='重要性,所有term重要性之和为1')

    class Meta:
        verbose_name = '词法分析结果'
        verbose_name_plural = '词法分析结果'


class SentimentAnalysis(models.Model):
    intent = models.ForeignKey(Intent, on_delete=models.CASCADE, related_name='sentiments', verbose_name='关联意图')

    label = models.IntegerField(verbose_name='情感分析倾向 0表示负向 1表示中性 2表示正向')
    pval = models.DecimalField(max_digits=5, decimal_places=4,
                               verbose_name='好评置信度-差评置信度, 越大表示分类结果的可靠性越高，0-1之间的值')

    class Meta:
        verbose_name = '情感分析结果'
        verbose_name_plural = '情感分析结果'


class AccessToken(models.Model):
    token = models.CharField(max_length=255, verbose_name='Access Token')
    client_id = models.CharField(max_length=64, verbose_name='Client ID')
    client_secret = models.CharField(max_length=64, verbose_name='Client Secret')
    expires_in = models.IntegerField(verbose_name='Access Token有效期(单位秒)')
    expires_date = models.DateTimeField(verbose_name='Access Token过期时间')

    def save(self, *args, **kwargs):
        self.expires_date = timezone.now() + timedelta(seconds=self.expires_in)
        super().save(*args, **kwargs)

    def get_valid_access_token(self):
        if self.is_valid():
            return self.token

        self.token, self.expires_in = self.request_access_token(self.client_id, self.client_secret)
        self.save()
        return self.token

    def is_valid(self):
        if not self.token:
            return False
        return timezone.now() < self.expires_date

    @staticmethod
    def create_or_update(client_id, client_secret):
        access_token, created = AccessToken.objects.get_or_create(client_id=client_id, client_secret=client_secret,
                                                                  defaults={'token': '', 'expires_in': 0})
        if not created and access_token.is_valid():
            return access_token

        token, expires_in = AccessToken.request_access_token(client_id, client_secret)
        if access_token:
            access_token.token = token
            access_token.expires_in = expires_in
            access_token.save()
        else:
            access_token = AccessToken.objects.create(token=token, expires_in=expires_in)
        return access_token

    @staticmethod
    def request_access_token(client_id, client_secret):
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }
        r = requests.post(url=url, params=params)
        if r.status_code != 200:
            logger.error('REQ TOKEN: {}, {}'.format(
                r.status_code,
                r.text),
            )
            return '', 0
        logger.info('Response: %s', r.text)
        response_json = r.json()
        if 'error' in response_json:
            logger.error('REQ TOKEN: {}, {}'.format(
                response_json.get("error"),
                response_json.get("error_description"),
            ))
            return '', 0
        logger.info('Response: %s', response_json)
        return response_json.get('access_token'), response_json.get('expires_in')
