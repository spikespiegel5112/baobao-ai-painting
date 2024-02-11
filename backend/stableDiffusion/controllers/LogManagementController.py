# from diffusers import StableDiffusionPipeline
import json
import os

from django.http import JsonResponse
from .CommonController import json_response_ensure_ascii

# from database import engine
# from stableDiffusion.models.Images import Images

dir_path = './chat-sd-logs/'


def get_log_list(request):
    print("get_log_list")
    global dir_path

    file_list = os.listdir(dir_path)
    print(file_list)
    result = []
    for item in file_list:
        result.append({
            'fileName': item
        })

    return json_response_ensure_ascii({
        'result': 'success',
        'data': result
    })


def open_log_file(request):
    global dir_path

    print("open_log_file")
    request_json = json.loads(request.body)

    file_name = request_json.get('fileName')
    file_name = str(dir_path) + str(file_name),
    file_name = file_name[0]
    print(file_name)

    # file = os.open(file_name, 'r')
    # os.close(file)

    with open(file_name, 'r+', encoding='utf-8') as f:
        content = f.read()
        return json_response_ensure_ascii({
            'result': 'success',
            'data': content
        })


def clean_log_by_file_name(request):
    print("clean_log_by_file_name")
    global dir_path

    print("open_log_file")
    request_json = json.loads(request.body)

    file_name = request_json.get('fileName')
    file_name = str(dir_path) + str(file_name),
    file_name = file_name[0]
    print(file_name)

    # file = os.open(file_name, 'r')
    # os.close(file)

    with open(file_name, 'r+', encoding='utf-8') as f:
        f.truncate()
        content = f.read()

        return json_response_ensure_ascii({
            'result': 'success',
            'data': content
        })


def update_log_by_file_name(request):
    print("update_log_by_file_name")
    global dir_path

    print("open_log_file")
    request_json = json.loads(request.body)

    file_name = request_json.get('fileName')
    file_name = str(dir_path) + str(file_name),
    file_name = file_name[0]
    print(file_name)

    # file = os.open(file_name, 'r')
    # os.close(file)

    with open(file_name, 'r+', encoding='utf-8') as f:
        f.truncate()
        content = f.read()

        return json_response_ensure_ascii({
            'result': 'success',
            'data': content
        })
