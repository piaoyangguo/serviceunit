import logging
import os
import random
import string

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from pydub import AudioSegment

from app.models import Intent, BotMergedSlot, IntentCandidate
from serviceunit.settings import BASE_DIR

logger = logging.getLogger(__name__)


def parse_intent(response_json, scene_id, query, user_id):
    session_id = response_json.get('result').get('session_id')
    schema = response_json.get('result').get('schema')
    qu_res = response_json.get('result').get('qu_res')

    # schema 匹配的意图, qu_res 候选意图
    intent = parse_schema(schema, query, scene_id, session_id, user_id)
    parse_qu_res(qu_res, intent)
    return intent


def parse_schema(schema, query, scene_id, session_id, user_id):
    intent = Intent.objects.create(user_id=user_id,
                                   query=query,
                                   current_qu_intent=schema.get('current_qu_intent'),
                                   intent_confidence=schema.get('intent_confidence'))

    #for slot in schema.get('bot_merged_slots'):
    #    BotMergedSlot.objects.create(intent=intent,
    #                                 confidence=slot.get('confidence'),
    #                                 original_word=slot.get('original_word'),
    #                                 normalized_word=slot.get('normalized_word'),
    #                                 length=slot.get('length'),
    #                                 offset=slot.get('offset'),
    #                                 type=slot.get('type'))
    return intent


def parse_qu_res(qu_res, intent):
    for candidate in qu_res.get('intent_candidates'):
        IntentCandidate.objects.create(intent=intent,
                                       intent_candidate=candidate.get('intent'),
                                       intent_confidence=candidate.get('intent_confidence'),
                                       intent_need_clarify=candidate.get('intent_need_clarify'),
                                       from_who=candidate.get('from_who'),
                                       match_info=candidate.get('match_info'))
        for slot in candidate.get('slots'):
            BotMergedSlot.objects.create(intent=intent, type=slot.get('type'),
                                         confidence=slot.get('confidence'),
                                         original_word=slot.get('original_word'),
                                         normalized_word=slot.get('normalized_word'),
                                         length=slot.get('length'),
                                         offset=slot.get('offset'),
                                         )

        # for lexical in qu_res.get('lexical_analysis'):
        #     LexicalAnalysis.objects.create(intent=intent,
        #                                    basic_word=lexical.get('basic_word'),
        #                                    type=lexical.get('type'),
        #                                    term=lexical.get('term'),
        #                                    weight=lexical.get('weight'))
        # sentiment = qu_res.get('sentiment_analysis')
        # SentimentAnalysis.objects.create(intent=intent, label=sentiment.get('label', 10), pval=sentiment.get('pval', 0))
