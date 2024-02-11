import json

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Dictionaries
from stableDiffusion.database import engine
from .CommonController import json_response_ensure_ascii


# from database import engine
# from stableDiffusion.models.Images import Images

def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(
        Dictionaries(
            title=request_json.get('title'),
            value=request_json.get('value'),
            category=request_json.get('category'),
        )
    )
    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful'
    })


def update(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)
    prompt_id = request_json.get('id')

    data = session.query(Dictionaries).filter_by(id=prompt_id).first()
    data.title = request_json.get('title')
    data.value = request_json.get('value')
    data.category = request_json.get('category')

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
    if type(request_json) == 'list':
        print(type(request_json))
        for item in request_json:
            data = session.query(Dictionaries).filter_by(id=item)
            print('已删除数据的数据量为:', request_json)
            data.delete()
    else:
        _id = request_json.get('id')
        data = session.query(Dictionaries).filter_by(id=_id)
        data.delete()

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })


def get(request):
    request_json = json.loads(request.body)
    category = request_json.get('category')

    pagination = request_json.get('pagination')
    if pagination is not None:
        page = pagination.get('page')
        size = pagination.get('size')
        offset = (page - 1) * size

    Session = sessionmaker(bind=engine)
    session = Session()

    total = session.query(func.count(Dictionaries.id)).scalar()

    if category is not None:
        data = session.query(Dictionaries).filter_by(category=category)
    else:
        data = session.query(Dictionaries)

    if pagination is not None:
        data = data.offset(offset).limit(size)
    else:
        data = data.all()

    result = []
    for item in data:
        result.append(item.to_json())

    session.commit()
    session.close()
    # result_json = result.to_json()
    return json_response_ensure_ascii({
        'result': 'successful',
        'pagination': {
            'total': total
        },
        'data': result
    })
