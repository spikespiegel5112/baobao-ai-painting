import json

import requests
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Users
from stableDiffusion.database import engine
from .AuthController import get_hwh5_access_token
from .CommonController import json_response_ensure_ascii


def get_user_detail_by_id(request):
    request_json = json.loads(request.body)
    user_id = request_json.get('id')

    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Users).filter_by(id=user_id).first()

    session.commit()
    session.close()

    return json_response_ensure_ascii({
        'result': 'successful',
        'data': result,

    })


def get(request):
    request_json = json.loads(request.body)
    pagination = request_json.get('pagination')
    if pagination is not None:
        page = pagination.get('page')
        size = pagination.get('size')
        offset = (page - 1) * size

    Session = sessionmaker(bind=engine)
    session = Session()
    total = session.query(func.count(Users.id)).scalar()

    if pagination is not None:
        data = session.query(Users).offset(offset).limit(size)
    else:
        data = session.query(Users).all()

    result = []

    for item in data:
        result.append(item.to_json())

    session.close()
    # result_json = result.to_json()
    return json_response_ensure_ascii({
        'result': 'successful',
        'pagination': {
            'total': total
        },
        'data': result,

    })


def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(
        Users(
            userNameCn=request_json.get('userNameCn'),
            userNameEn=request_json.get('userNameEn'),
            welinkUserId=request_json.get('welinkUserId'),
            welinkTenantId=request_json.get('welinkTenantId'),
            guestUserId=request_json.get('guestUserId'),
            role=request_json.get('role'),
        )

    )

    session.commit()
    session.close()

    return json_response_ensure_ascii({
        'result': 'successful',
    })


def update(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)
    user_id = request_json.get('id')
    if user_id is None:
        return json_response_ensure_ascii({
            'result': 'error',
            'message': '没有传递用户ID'
        }, status=400)

    data = session.query(Users).filter_by(id=user_id).first()
    print('=====type(request_json)=====')
    print(type(request_json))
    print(type(data))

    if request_json.get('userNameCn'):
        data.userNameCn = request_json.get('userNameCn')
    if request_json.get('userNameCn'):
        data.userNameEn = request_json.get('userNameEn')
    if request_json.get('welinkUserId'):
        data.welinkUserId = request_json.get('welinkUserId')
    if request_json.get('welinkTenantId'):
        data.welinkTenantId = request_json.get('welinkTenantId')
    if request_json.get('guestUserId'):
        data.guestUserId = request_json.get('guestUserId')
    if request_json.get('role'):
        data.role = request_json.get('role')
    if request_json.get('settings'):
        settings = request_json.get('settings')
        data.settings = json.dumps(settings)

    result_json = data.to_json()

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
        'data': result_json
    })


def delete(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)

    for item in request_json:
        data = session.query(Users).filter_by(id=item)
        print('已删除数据的数据量为:', request_json)
        data.delete()

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })


def get_welink_user_detail(request):
    accessTokenInfoData = get_hwh5_access_token()
    accessTokenInfoData = accessTokenInfoData.json()
    print('=====accessTokenInfoData=====')
    print(accessTokenInfoData)
    request_json = json.loads(request.body)
    corpUserId = request_json.get('corpUserId')
    userId = request_json.get('userId')
    mobileNumber = request_json.get('mobileNumber')
    if accessTokenInfoData is not None:
        url = 'https://open.welink.huaweicloud.com/api/contact/v2/user/detail'
        headers = {
            'Accept-Charset': 'UTF-8',
            'Content-Type': 'application/json',
            'lang': 'zh',
            "x-wlk-Authorization": accessTokenInfoData.get('access_token'),
        }
        user_detail_data = requests.post(url, headers=headers, json={
            "corpUserId": corpUserId,
            "userId": userId,
            "mobileNumber": mobileNumber,
        })
        print('=====user_detail_data=====')
        print(user_detail_data.json())

        return json_response_ensure_ascii({
            'result': 'successful',
            "data": user_detail_data.json()
        })
    else:
        return json_response_ensure_ascii({
            'result': 'error',
            "error": 'nonono'
        }, status=400)


def get_user_detail_by_app_user_id(request):
    request_json = json.loads(request.body)
    welink_user_id = request_json.get('welinkUserId')
    welink_tenant_id = request_json.get('welinkTenantId')
    guest_user_id = request_json.get('guestUserId')

    Session = sessionmaker(bind=engine)
    session = Session()

    if welink_user_id is not None:
        user = session.query(Users).filter_by(welinkUserId=welink_user_id).first()
        if user:
            response_json = json_response_ensure_ascii({
                'result': 'successful',
                'message': "用户已存在",
                'data': {
                    'exist': True,
                    'welinkUserId': user.welinkUserId,
                    'guestUserId': user.guestUserId,
                    'id': user.id,
                    'settings': user.settings,
                }

            })
        else:
            response_json = json_response_ensure_ascii({
                'result': 'successful',
                'message': "用户不存在",
                'data': {
                    'exist': False,
                }

            })
    elif guest_user_id is not None:
        user = session.query(Users).filter_by(guestUserId=guest_user_id).first()
        if user:
            response_json = json_response_ensure_ascii({
                'result': 'successful',
                'message': "用户已存在",
                'data': {
                    'exist': True,
                    'welinkUserId': user.welinkUserId,
                    'guestUserId': user.guestUserId,
                    'id': user.id,
                    'settings': user.settings,
                }
            })
        else:
            response_json = json_response_ensure_ascii({
                'result': 'successful',
                'message': "用户不存在",
                'data': {
                    'exist': False,
                }
            })
    else:
        response_json = json_response_ensure_ascii({
            'result': 'successful',
            'message': "缺少必要的参数"
        }, status=400)

    session.close()
    return response_json
