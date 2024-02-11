import hashlib
import json
from datetime import datetime

import requests

from .CommonController import json_response_ensure_ascii

expires_in = 0
access_token_timestamp = 0
accessTokenInfo = None

client_id = ""
client_secret = ""


def _check_expire():
    current_timestamp = datetime.now().timestamp() * 1000
    expire_timestamp = access_token_timestamp + (expires_in - 300) * 1000
    result = expire_timestamp - current_timestamp <= 0
    print('==========checkExpire==========')
    print("expireTimeStamp++++", expire_timestamp)
    print("currentTimeStamp++++", current_timestamp)
    print("expireTimeStamp - currentTimeStamp++++", expire_timestamp - current_timestamp)
    print("checkExpire result++++", result)
    return result


async def generate_signature(request):
    print('==========generate_signature==========')
    global accessTokenInfo
    global access_token_timestamp

    try:

        request_json = json.loads(request.body)

        if _check_expire() is True:
            accessTokenInfo = _get_hwh5_access_token_promise()
            print('=====accessTokenInfo 1=====')
            print(accessTokenInfo)
            access_token_timestamp = datetime.now().timestamp() * 1000

        access_token = accessTokenInfo["access_token"]
        # expires_in = accessTokenInfo["expires_in"]
        expires_in = 900
        url = request_json.get('url')

        time_stamp = str(int(datetime.now().timestamp()))
        nonce_str = "123456"
        signature = ""

        if access_token is None:
            return json_response_ensure_ascii({
                'result': 'error',
                'data': accessTokenInfo
            }, status=400)

        jstickets_info = _get_hwh5_js_api_ticket_promise(accessTokenInfo)
        if jstickets_info["code"] == "1000":
            accessTokenInfo = None
        jstickets = jstickets_info["jstickets"]

        # print("accessTokenInfo+++++", accessTokenInfo)
        print("jsticketsInfo+++++", jstickets_info)
        print("url+++++", url)

        if accessTokenInfo["code"] == "0" and jstickets_info["code"] == "0":
            plain = (
                f"jsapi_ticket={jstickets}"
                f"&noncestr={nonce_str}"
                f"&timestamp={time_stamp}"
                f"&url={url}"
            )

            hash_object = hashlib.sha256(plain.encode())
            signature = hash_object.hexdigest()

            return json_response_ensure_ascii({
                'result': 'successful',
                'data': {
                    "result": {"clientId": client_id, "timeStamp": time_stamp,
                               "nonceStr": nonce_str, "signature": signature},
                    "accessTokenInfo": accessTokenInfo,
                    "jsticketsInfo": jstickets_info,
                    "url": url,
                }
            })

        else:
            return json_response_ensure_ascii({
                'result': 'successful',
                'data': {
                    "accessTokenInfo": accessTokenInfo,
                    "jsticketsInfo": jstickets_info,
                    "url": url,
                }
            })

    except Exception as error:
        # print(error)
        return json_response_ensure_ascii({
            'result': 'error',
            "error": str(error),
        }, status=400)


def _get_hwh5_access_token_promise():
    print('==========_get_hwh5_access_token_promise==========')

    url = "https://open.welink.huaweicloud.com/api/auth/v2/tickets"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "client_id": client_id,  # 请在此处替换为正确的值
        "client_secret": client_secret,  # 请在此处替换为正确的值
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print('accessTokenInfo.data+++++', response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        # print(e)
        print('error _get_hwh5_access_token_promise')
        raise e


def _get_hwh5_js_api_ticket_promise(access_token_info):
    access_token = access_token_info["access_token"]

    url = "https://open.welink.huaweicloud.com/api/auth/v1/jstickets"

    headers = {
        "x-wlk-Authorization": access_token,
    }

    try:
        response = requests.get(url, headers=headers)
        # print(response.json())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        # print(e)
        raise e


def get_hwh5_access_token():
    print('==========get_hwh5_access_token==========')
    url = "https://open.welink.huaweicloud.com/api/auth/v2/tickets"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print('accessTokenInfo.data+++++', response.json())
        return response
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)


async def get_hwh5_user_id_by_auth_code(request):
    request_json = json.loads(request.body)
    global access_token_timestamp
    global accessTokenInfo

    try:
        if _check_expire() is True:
            accessTokenInfo = _get_hwh5_access_token_promise()
            print('=====accessTokenInfo 2=====')
            print(accessTokenInfo)
            access_token_timestamp = datetime.now().timestamp() * 1000

        access_token = accessTokenInfo["access_token"]

        url = "https://open.welink.huaweicloud.com/api/auth/v2/userid"

        headers = {
            "Content-Type": "application/json",
            "x-wlk-Authorization": access_token,
        }

        params = {
            "code": request_json.get('code')
        }

        response = requests.get(url, headers=headers, params=params)
        print('=====response = requests.get(url, headers=headers, params=params)=====')
        print(response.json())
        response.raise_for_status()

        return json_response_ensure_ascii({
            'result': 'successful',
            "data": response.json(),
        })

    except requests.exceptions.RequestException as error:
        # print(error)
        return json_response_ensure_ascii({
            'result': 'error',
            "error": str(error)
        }, status=400)
