import time

from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker

from stableDiffusion.database import Models
from stableDiffusion.database import engine
import asyncio
import os
import platform


def generate_file_name(num_inference_steps):
    if num_inference_steps is None:
        num_inference_steps_str = ''
    else:
        num_inference_steps_str = '_' + str(num_inference_steps)
    timestamp_str = str(int(time.time()))
    file_name = timestamp_str + num_inference_steps_str + '.jpg'
    return file_name


def get_architecture_by_os():
    current_os = platform.system()
    print('=====platform======')
    print(current_os)
    if current_os is 'Darwin':
        result = 'mps'
    else:
        result = 'cuda'
    return result


def get_repo_id(repo_name):
    print('========get_repo_id========')
    print(repo_name)
    Session = sessionmaker(bind=engine)
    session = Session()
    data = session.query(Models).filter_by(repoName=repo_name)
    session.commit()
    session.close()
    if data.first():
        return data.first()
    else:
        return None


def get_pytorch_device():
    result = 'cuda'
    if platform.system() == 'Darwin':
        result = 'mps'
    return result


def json_response_ensure_ascii(data, status=None):
    if status is None:
        status = 200
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii':
                                                                    False})


def get_device_name():
    result = 'cuda'
    # 针对Apple silicon芯片
    if platform.system() == 'Darwin':
        result = 'mps'
    return result
