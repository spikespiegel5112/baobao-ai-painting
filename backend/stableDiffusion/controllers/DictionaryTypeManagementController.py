import json

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import DictionaryTypes
from stableDiffusion.database import engine
from .CommonController import json_response_ensure_ascii


# from database import engine
# from stableDiffusion.models.Images import Images

def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(
        DictionaryTypes(
            title=request_json.get('title'),
            value=request_json.get('value'),
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

    data = session.query(DictionaryTypes).filter_by(id=prompt_id).first()
    data.title = request_json.get('title')
    data.value = request_json.get('value')
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
    prompt_id = request_json.get('id')
    data = session.query(DictionaryTypes).filter_by(id=prompt_id)
    data.delete()
    print('已删除数据的数据量为:', data)

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
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

    total = session.query(func.count(DictionaryTypes.id)).scalar()

    if pagination is not None:
        data = session.query(DictionaryTypes).offset(offset).limit(size)
    else:
        data = session.query(DictionaryTypes).all()

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
