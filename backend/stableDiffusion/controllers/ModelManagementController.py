import json

from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Models
from stableDiffusion.database import engine
from .CommonController import json_response_ensure_ascii


# from database import engine

def create(request):
    request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(
        Models(
            title=request_json.get('title'),
            repoName=request_json.get('repoName'),
            envPath=request_json.get('envPath'),
            useCuda=request_json.get('useCuda'),
            defaultSettings=request_json.get('defaultSettings'),
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

    data = session.query(Models).filter_by(id=prompt_id).first()
    data.title = request_json.get('title')
    data.repoName = request_json.get('repoName')
    data.envPath = request_json.get('envPath')
    data.useCuda = request_json.get('useCuda')
    data.defaultSettings = request_json.get('defaultSettings')
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
        data = session.query(Models).filter_by(id=item).delete()
        print('已删除数据的数据量为:', data)

    session.commit()
    session.close()
    return json_response_ensure_ascii({
        'result': 'successful',
    })


def get(request):
    # request_json = json.loads(request.body)
    Session = sessionmaker(bind=engine)
    session = Session()
    data = session.query(Models).all()

    result = []
    for item in data:
        result.append(item.to_json())

    session.commit()
    session.close()
    # result_json = result.to_json()
    return json_response_ensure_ascii({
        'result': 'successful',
        'data': result
    })
