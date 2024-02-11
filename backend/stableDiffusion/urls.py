"""
URL configuration for stableDiffusion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from . import views
from .controllers import AuthController
from .controllers import DictionaryManagementController
from .controllers import DictionaryTypeManagementController
from .controllers import Txt2ImgController
from .controllers import ImageManagementController
from .controllers import LogManagementController
from .controllers import MBartController
from .controllers import ModelManagementController
from .controllers import PromptCategoryManagementController
from .controllers import PromptManagementController
from .controllers import UserController

urlpatterns = [
    # path('', admin.site.urls),
    # 生产环境下对外提供静态文件的url
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('testJson/', views.test_json, name='testJson'),
    path('txt2Img/', Txt2ImgController.handle_txt_2_img, name='txt2Img'),
    path('addQueue/', Txt2ImgController.handle_add_queue, name='addQueue'),
    path('triggerTxt2ImgByQueue/', Txt2ImgController.trigger_txt_2_img_by_queue,
         name='triggerTxt2ImgByQueue'),

    path('getLastImageData/', Txt2ImgController.get_last_image_data,
         name='getLastImageData'),

    path('getCancellingProgress/', Txt2ImgController.get_cancelling_progress,
         name='getCancellingProgress'),
    path('getGenerationStatus/', Txt2ImgController.get_generation_status,
         name='getGenerationStatus'),
    path('checkQueueByUserId/', Txt2ImgController.handle_check_queue_by_user_id,
         name='checkQueueByUserId'),
    path('deleteQueue/', Txt2ImgController.delete_queue,
         name='deleteQueue'),

    path('cancelGeneration/', Txt2ImgController.cancel_generation,
         name='cancelGeneration'),

    path('translator/', MBartController.translator,
         name='translator'),

    path('saveBase64AsImageFile/', ImageManagementController.save_base64_as_image_file,
         name='saveBase64AsImageFile'),
    path('saveImageToAlbum/', ImageManagementController.save_image_to_album,
         name='saveImageToAlbum'),

    path('promptManagement/create/', PromptManagementController.create, name='create'),
    path('promptManagement/get/', PromptManagementController.get, name='get'),
    path('promptManagement/update/', PromptManagementController.update, name='update'),
    path('promptManagement/delete/', PromptManagementController.delete, name='delete'),
    path('promptManagement/setAllToPositive/',
         PromptManagementController.set_all_to_positive,
         name='set_all_to_positive'),

    path('DictionaryTypeManagement/create/',
         DictionaryTypeManagementController.create,
         name='create'),
    path('dictionaryTypeManagement/get/',
         DictionaryTypeManagementController.get, name='get'),
    path('DictionaryTypeManagement/update/',
         DictionaryTypeManagementController.update,
         name='update'),
    path('DictionaryTypeManagement/delete/',
         DictionaryTypeManagementController.delete,
         name='delete'),

    path('dictionaryManagement/create/', DictionaryManagementController.create,
         name='create'),
    path('dictionaryManagement/get/', DictionaryManagementController.get, name='get'),
    path('dictionaryManagement/update/', DictionaryManagementController.update,
         name='update'),
    path('dictionaryManagement/delete/', DictionaryManagementController.delete,
         name='delete'),

    path('promptCategoryManagement/create/', PromptCategoryManagementController.create,
         name='create'),
    path('promptCategoryManagement/get/', PromptCategoryManagementController.get,
         name='get'),
    path('promptCategoryManagement2/get/', PromptCategoryManagementController.get,
         name='get'),
    path('promptCategoryManagement/update/', PromptCategoryManagementController.update,
         name='update'),
    path('promptCategoryManagement/delete/', PromptCategoryManagementController.delete,
         name='delete'),

    path('imageManagement/create/', ImageManagementController.create,
         name='create'),
    path('imageManagement/get/', ImageManagementController.get, name='get'),
    path('imageManagement/update/', ImageManagementController.update,
         name='update'),
    path('imageManagement/delete/', ImageManagementController.delete,
         name='delete'),
    path('imageManagement/setMultipleUserId/',
         ImageManagementController.set_multiple_user_id,
         name='set_multiple_user_id'),
    path('imageManagement/setImageToPublic/',
         ImageManagementController.set_image_to_public,
         name='set_image_to_public'),

    path('modelManagement/create/', ModelManagementController.create,
         name='create'),
    path('modelManagement/get/', ModelManagementController.get, name='get'),
    path('modelManagement/update/', ModelManagementController.update,
         name='update'),
    path('modelManagement/delete/', ModelManagementController.delete,
         name='delete'),

    path('logManagement/getLogList/', LogManagementController.get_log_list,
         name='get_log_list'),
    path('logManagement/getLogFile/', LogManagementController.open_log_file,
         name='open_log_file'),
    path('logManagement/cleanLogByFileName/',
         LogManagementController.clean_log_by_file_name,
         name='clean_log_by_file_name'),

    # AuthController

    path('auth/generateSignature/',
         AuthController.generate_signature,
         name='generate_signature'),
    path('auth/getHwh5AccessToken/',
         AuthController.get_hwh5_access_token,
         name='get_hwh5_access_token'),
    path('auth/getHWH5UserIdByAuthCode/',
         AuthController.get_hwh5_user_id_by_auth_code,
         name='get_hwh5_user_id_by_auth_code'),

    # UserController

    path('user/getUserDetailByAppUserId/',
         UserController.get_user_detail_by_app_user_id,
         name='get_user_detail_by_app_user_id'),

    path('user/getWelinkUserDetail/',
         UserController.get_welink_user_detail,
         name='get_welink_user_detail'),

    path('user/getUserDetailById/',
         UserController.get_user_detail_by_id,
         name='get_user_detail_by_id'),

    path('user/create/',
         UserController.create,
         name='create'),
    path('user/update/',
         UserController.update,
         name='update'),
    path('user/get/',
         UserController.get,
         name='get'),
    path('user/delete/',
         UserController.delete,
         name='delete'),

]
