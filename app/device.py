import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor

from hyper import HTTP20Connection, HTTP20Response

from app.models import AccessToken

logger = logging.getLogger()

env = {}
executor = ThreadPoolExecutor()


def get_access_token():
    if 'access_token' not in env:
        env['access_token'] = AccessToken.create_or_update('6CiaefDPnOTQcajaGjWr6R8vIjTRvtIj',
                                                           'F0VlkjtnsDYMrgiTwjCzy6LjuqnOhdGh')
    return env['access_token'].get_valid_access_token()


def get_headers():
    return {
        'authorization': 'Bearer ' + get_access_token(),
        'dueros-device-id': '1001',
        # 'user-agent': 'version/1',
    }


def directives(conn: HTTP20Connection):
    stream = conn.request('GET', '/dcs/v1/directives', headers=get_headers())
    while True:
        for push in conn.get_pushes(stream):
            logger.info('Directive: %s', push.push)
        time.sleep(2)
    logger.info('DIRECTIVE QUIT')


def ping(conn: HTTP20Connection):
    stream = conn.request('GET', '/dcs/v1/ping', headers=get_headers())
    response = conn.get_response(stream)
    if response.status != 200:
        get_conn(force_create=True)
    logger.info('PING %s', response.status)

    time.sleep(60)
    executor.submit(ping, conn)


def get_conn(force_create=False) -> HTTP20Connection:
    if force_create or 'conn' not in env:
        env['conn'] = HTTP20Connection('dueros-h2.baidu.com', enable_push=True)
        executor.submit(directives, env['conn'])
        executor.submit(ping, env['conn'])
    return env['conn']


def assemble_body(msg_id: str, dlg_id: str, boundary: str, audio: bytes):
    msg_header = 'Content-Disposition:form-data; name="metadata"\r\nContent-Type:application/json; charset=UTF-8'
    msg_body = json.dumps({
        "clientContext": [0, 0, 1, 0],
        "event": {
            "header": {
                "namespace": "ai.dueros.device_interface.voice_input",
                "name": "ListenStarted",
                "messageId": msg_id,
                "dialogRequestId": dlg_id
            },
            "payload": {
                "format": "AUDIO_L16_RATE_16000_CHANNELS_1"
            }
        }
    })
    aud_header = 'Content-Disposition:form-data; name="audio"\r\nContent-Type:application/octet-stream'
    payload = f'--{boundary}\r\n{msg_header}\r\n\r\n{msg_body}\r\n\r\n--{boundary}\r\n{aud_header}\r\n\r\n'.encode(
        'utf8') + audio + f'\r\n--{boundary}--'.encode('utf8')
    return payload


def update_event(audio: bytes):
    msg_id = f'm{int(time.time() * 1000)}{random.randint(10, 99)}'
    dlg_id = f'm{int(time.time() * 1000)}{random.randint(10, 99)}'
    boundary = '__abc__'

    headers = {'content-type': f'multipart/form-data; boundary={boundary}'}
    headers.update(get_headers())
    body = assemble_body(msg_id, dlg_id, boundary, audio)

    conn = get_conn()
    stream = conn.request('POST', '/dcs/v1/events', headers=headers, body=body)
    response: HTTP20Response = conn.get_response(stream)
    print(response.status)
    for k, v in response.headers.items():
        print(k, v)
    content = response.read()
    print(content)
    return content


def exit_thread():
    print('exit start')
    executor.shutdown()
    print('exit end')


import atexit

atexit.register(exit_thread)
