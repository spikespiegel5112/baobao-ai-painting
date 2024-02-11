import json

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Prompts
from stableDiffusion.database import engine
from .CommonController import json_response_ensure_ascii


# from database import engine
# from stableDiffusion.models.Images import Images


def get(request):
    request_json = json.loads(request.body)

    pagination = request_json.get('pagination')
    if pagination is not None:
        page = pagination.get('page')
        size = pagination.get('size')
        offset = (page - 1) * size

    Session = sessionmaker(bind=engine)
    session = Session()

    total = session.query(func.count(Prompts.id)).scalar()

    if str(request.body) == "b''" or str(request.body) == "b'{}'":
        direction = 'all'
    else:
        request_json = json.loads(request.body)
        direction = request_json.get('direction')
        direction = str.lower(direction)

    if direction == 'all':
        data = session.query(Prompts)
    else:
        data = session.query(Prompts).filter_by(direction=direction)

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
        'data': result,
    })


def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(
        Prompts(
            title=request_json.get('title'),
            value=request_json.get('value'),
            category=request_json.get('category'),
            direction=request_json.get('direction'),
        )

    )

    session.commit()
    session.close()

    return json_response_ensure_ascii({
        'result': 'successful'
    })


def set_all_to_positive(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)

    data = session.query(Prompts).all()
    for item in data:
        item.direction = request_json.get('direction')

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })


def update(request):
    Session = sessionmaker(bind=engine)
    session = Session()

    request_json = json.loads(request.body)
    prompt_id = request_json.get('id')

    data = session.query(Prompts).filter_by(id=prompt_id).first()
    data.title = request_json.get('title')
    data.value = request_json.get('value')
    data.category = request_json.get('category')
    data.direction = request_json.get('direction')
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
        data = session.query(Prompts).filter_by(id=item).delete()
        print('已删除数据的数据量为:', data)

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })
