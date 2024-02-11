from django.http import HttpResponse

from .controllers.Txt2ImgController import *


def hello(request):
    return HttpResponse('Hello world')


def test_json(request):
    if request.method == 'POST':
        # 处理POST请求的逻辑代码
        data = request.POST.get('data')  # 获取POST请求的参数
        # 其他处理逻辑...

        # 返回响应
    response_data = {'message': '成功接收到POST请求', 'data': data}
    return JsonResponse(response_data)
