import base64
import datetime
import json
import os
from io import BytesIO

from PIL import Image
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Images, engine
from .CommonController import json_response_ensure_ascii, generate_file_name


def save_image_to_album(request):
    print('=====save_image_to_album=====')
    request_json = json.loads(request.body)
    _num_inference_steps = request_json.get('numInferenceSteps')
    otherSettings = json.dumps(request_json.get('otherSettings'))
    base64Data = request_json.get('base64Data'),

    file_name = generate_file_name(_num_inference_steps)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(
        Images(fileName=file_name,
               customPositivePrompt=request_json.get('customPositivePrompt'),
               positivePrompt=request_json.get('positivePrompt'),
               customNegativePrompt=request_json.get('customNegativePrompt'),
               negativePrompt=request_json.get('negativePrompt'),
               width=request_json.get('width'),
               height=request_json.get('height'),
               seed=request_json.get('seed'),
               createdAt=datetime.datetime.now(),
               otherSettings=otherSettings,
               userId=request_json.get('userId'),
               welinkUserId=request_json.get('welinkUserId'),
               guestUserId=request_json.get('guestUserId'),
               userComesFrom=request_json.get('userComesFrom'),
               ))

    session.commit()
    session.close()
    save_base64_as_image_file(request, file_name)
    return json_response_ensure_ascii({
        'result': 'successful'
    })


def save_base64_as_image_file(request, file_name):
    print('=====save_base64_as_image_file=====')
    # 从POST请求中获取Base64数据
    request_byte = request.body
    request_json = json.loads(request_byte)

    _base64_data = request_json.get('base64Data')
    image_type_dictionary = ['data:image/jpeg;base64,', 'data:image/png;base64,',
                             'data:image/gif;base64,']
    for item in image_type_dictionary:
        if item in _base64_data:
            _base64_data = _base64_data.replace(item, '')

    print(file_name)
    try:
        # 解码Base64数据
        image_data = base64.b64decode(_base64_data)

        # 创建一个BytesIO对象以读取图像数据
        image_buffer = BytesIO(image_data)

        # 打开图像并保存为JPEG文件
        image = Image.open(image_buffer)
        image = image.convert('RGB')
        image.save(
            './output/' + file_name, 'JPEG')
        print('=====save_base64_as_image_file ./output/' + file_name + ' JPEG=====')
        return json_response_ensure_ascii({
            'result': 'successful',
            'fileName': file_name
        })
    except Exception as error:
        print(error)
        print("解码并保存图像时出错:", str(error))
        return json_response_ensure_ascii({
            'result': 'failed',
            'message': str(error)
        }, status=400)


def get(request):
    request_json = json.loads(request.body)

    pagination = request_json.get('pagination')
    comesFrom = request_json.get('comesFrom')
    welinkUserId = request_json.get('welinkUserId')
    guestUserId = request_json.get('guestUserId')
    is_public = request_json.get('isPublic')
    user_id = request_json.get('userId')
    if pagination is not None:
        page = pagination.get('page')
        size = pagination.get('size')
        offset = (page - 1) * size

    Session = sessionmaker(bind=engine)
    session = Session()
    if comesFrom is None:
        total = session.query(func.count(Images.id)).scalar()
    if is_public is True:
        data = session.query(Images).filter_by(isPublic=is_public)
    else:
        if user_id is not None:
            data = session.query(Images).filter_by(userId=user_id)
        else:
            data = session.query(Images)

    data = data.order_by(desc(Images.createdAt))
    total = data.count()

    if pagination is not None:
        data = data.offset(offset).limit(size)
    else:
        data = data.all()
    result = []
    for item in data:
        result.append(item.to_json())

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
        'pagination': {
            'total': total
        },
        'data': result
    })


def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.add(
        Images(
            fileName=request_json.get('fileName'),
            customPositivePrompt=request_json.get('customPositivePrompt'),
            positivePrompt=request_json.get('positivePrompt'),
            customNegativePrompt=request_json.get('customNegativePrompt'),
            negativePrompt=request_json.get('negativePrompt'),
            width=request_json.get('width'),
            height=request_json.get('height'),
            seed=request_json.get('height'),
            otherSettings=request_json.get('otherSettings'),
            welinkUserId=request_json.get('welinkUserId'),
            guestUserId=request_json.get('guestUserId'),

            createdAt=datetime.datetime.now()
        )

    )

    session.commit()
    session.close()

    return json_response_ensure_ascii({
        'result': 'successful'
    })


def set_multiple_user_id(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    data = session.query(Images).all()
    for item in data:
        item.userComesFrom = 'welink'

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })


def set_image_to_public(request):
    request_json = json.loads(request.body)
    image_id = request_json.get('id')
    is_public = request_json.get('isPublic')
    Session = sessionmaker(bind=engine)
    session = Session()

    data = session.query(Images).filter_by(id=image_id).first()
    data.isPublic = is_public

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
        'id': image_id
    })


def update(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)
    prompt_id = request_json.get('id')

    data = session.query(Images).filter_by(id=prompt_id).first()
    data.fileName = request_json.get('fileName')
    data.customPositivePrompt = request_json.get('customPositivePrompt')
    data.positivePrompt = request_json.get('positivePrompt')
    data.customNegativePrompt = request_json.get('customNegativePrompt')
    data.negativePrompt = request_json.get('negativePrompt')
    data.width = request_json.get('width')
    data.height = request_json.get('height')
    data.seed = request_json.get('seed')
    data.otherSettings = request_json.get('otherSettings')
    data.welinkUserId = request_json.get('welinkUserId')
    data.welinkUserId = request_json.get('welinkUserId')
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
        data = session.query(Images).filter_by(id=item)
        for item2 in data:
            file_name = item2.to_json()
            print(file_name['fileName'])
            file_path = './output/' + file_name['fileName']
            if os.path.exists(file_path):
                os.remove('./output/' + file_name['fileName'])
            data.delete()

        print('已删除数据的数据量为:', data)
    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })
