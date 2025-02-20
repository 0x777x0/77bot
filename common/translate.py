import json
import logging

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models

from common.cache import redis
from util.date_util import get_timestamp
from util.md5_util import md5_util


def translate(text):
    text = text.replace('\r\n', '')
    text = text.replace('\r', '')
    if not text:
        return ''
    result = _get_translate_cache(text)
    if result:
        return result

    try:
        start = get_timestamp()
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential("AKIDlQ7g7QaiiWBE8wbfaLvLafkkdKo6FE5j", "XvBF4h7KNK7kBQREwWyJVYUME3ueKtLd")
        http_profile = HttpProfile()
        http_profile.endpoint = "tmt.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = tmt_client.TmtClient(cred, "ap-chengdu", client_profile)

        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": "auto",
            "Target": "zh",
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        resp = client.TextTranslate(req)
        logging.info("monitor ===> translate, elapse: %s", get_timestamp() - start)
        logging.info("translate result, text:%s, result:%s", text, resp.to_json_string())

        translate_result = resp.TargetText
        _set_translate_cache(text, translate_result)
        return translate_result

    except Exception as err:
        logging.error("translate error, text:%s, err:%s", text, err)
        return ''


def _set_translate_cache(text, translate_result):
    md5_hash = md5_util(text)
    key = "translate:" + md5_hash
    redis.set(key, translate_result, ex=7 * 24 * 60 * 60)
    return

def _get_translate_cache(text):
    md5_hash = md5_util(text)
    key = "translate:" + md5_hash
    return redis.get(key)

# print(translate("CChat with someone for two minutes.\r\nTry to figure out if it was a human or an AI bot.\r\nThink you can tell the difference?"))
