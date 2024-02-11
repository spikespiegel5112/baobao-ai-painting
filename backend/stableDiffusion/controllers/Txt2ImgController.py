import base64
import datetime
import gc
import json
import os
import platform
import time
from io import BytesIO
from PIL import Image

import langid

from diffusers import AutoPipelineForText2Image, StableDiffusionPipeline, StableDiffusionXLPipeline, LCMScheduler

from diffusers.models import AutoencoderKL
from sqlalchemy.orm import sessionmaker
from torch import torch
from torchvision import transforms

from stableDiffusion.database import Queue
from stableDiffusion.database import engine
from .CommonController import json_response_ensure_ascii, get_repo_id, get_device_name
from .SamplerChecker import sampler_checker
from .MBartController import _translator
from .base64_image_data1 import base64_image_data1
from .base64_image_data2 import base64_image_data2

# from database import engine
# from stableDiffusion.models.Images import Images

is_test_mode = False
execution_duration = 5
cooling_down_duration = 10
temp_file_name = ''
base64_data = None
progress = 0
on_progress = False
cancelling_flag = False
on_cooling_down = False
cooling_down_deadline_timestamp = None
cooling_down_count_down = None
initialized_flag = False
generating_base_index = None
generating_base_steps = None
generating_refiner_index = None
generating_refiner_steps = None
on_progress_session_id = None
last_session_id = None
used_seed = None
temporary_latent_base64 = None
num_inference_steps = None
current_timestep_base = None
current_timestep_refiner = None
current_generating_user_id = None
current_generating_user_comes_from = None
next_image_data_name = None
is_same_user = None
base_repo_id_data = None
pytorch_device = ''

sdxl_vae_repo_id_data = get_repo_id('sdxl-vae')
sdxl_vae_repo_id = sdxl_vae_repo_id_data.envPath + sdxl_vae_repo_id_data.repoName
# base_repo_id = './models/vae/' + 'diffusion_pytorch_model.fp16'
vae = AutoencoderKL.from_pretrained(sdxl_vae_repo_id)


# def delete_queue(request):


def trigger_txt_2_img_by_queue(request):
    request_bytes = request.body
    request_json = json.loads(request_bytes)
    user_id = request_json.get('userId')
    Session = sessionmaker(bind=engine)
    session = Session()
    all_data = session.query(Queue).all()
    data = session.query(Queue).first()
    print('=====trigger_txt_2_img_by_queue=====')
    # print(len(data))
    length = len(all_data)
    if length == 0:
        return json_response_ensure_ascii({
            "message": '待生成队列为空',
            'code': 10002,
        })
    time.sleep(10)
    fist_data_index = 0
    last_data_index = length - 1
    # execute_data = data[fist_data_index]
    execute_data = data

    # execute_data = execute_data.to_json()
    other_settings_string = execute_data.otherSettings
    other_settings = json.loads(other_settings_string)
    print('=====other_settings=====')
    print(other_settings)
    params = {
        'positive_prompt': execute_data.positivePrompt,
        'custom_positive_prompt': execute_data.customPositivePrompt,
        'negative_prompt': execute_data.negativePrompt,
        'custom_negative_prompt': execute_data.customNegativePrompt,
        'num_inference_steps': execute_data.numInferenceSteps,
        'width': execute_data.width,
        'height': execute_data.height,
        'session_id': execute_data.sessionId,
        'num_inference_steps_refiner': other_settings.get('numInferenceStepsRefiner',
                                                          ''),
        'seed': execute_data.seed,

        'enable_attention_slicing': other_settings.get('enableAttentionSlicing', ''),
        'enable_vae_slicing': other_settings.get('enableVaeSlicing', ''),
        'enable_vae_tiling': other_settings.get('enableVaeTiling', ''),
        'enable_xformers_memory_efficient_attention': other_settings.get(
            'enableXformersMemoryEfficientAttention', ''),

        # welink_user_id : last_execute_data.welinkUserId')
        'current_generating_user_comes_from': execute_data.userComesFrom,
        # 'current_generating_user_id': other_settings['appUserId'],
    }
    # queue_data = session.query(Queue).filter_by(userId=userId).first()
    print('=====params=====')
    print(params)
    session.delete(data)

    session.commit()
    session.close()
    return txt_2_img(params)


def handle_txt_2_img(request):
    global on_progress_session_id
    request_bytes = request.body
    request_json = json.loads(request_bytes)
    params = {
        'positive_prompt': request_json.get('positivePrompt'),
        'custom_positive_prompt': request_json.get('customPositivePrompt'),
        'negative_prompt': request_json.get('negativePrompt'),
        'custom_negative_prompt': request_json.get('customNegativePrompt'),
        'num_inference_steps': request_json.get('numInferenceSteps'),
        'width': request_json.get('width'),
        'height': request_json.get('height'),
        'session_id': request_json.get('sessionId'),
        'num_inference_steps_refiner': request_json.get('numInferenceStepsRefiner'),
        'seed': request_json.get('seed'),
        'useFp32': request_json.get('useFp32'),
        'useLcmLora': request_json.get('useLcmLora'),

        'enable_attention_slicing': request_json.get('enableAttentionSlicing'),
        'enable_vae_slicing': request_json.get('enableVaeSlicing'),
        'enable_vae_tiling': request_json.get('enableVaeTiling'),
        'enable_xformers_memory_efficient_attention': request_json.get(
            'enableXformersMemoryEfficientAttention'),

        # welink_user_id : request_json.get('welinkUserId')
        'current_generating_user_comes_from': request_json.get('userComesFrom'),
        'current_generating_user_id': request_json.get('userId'),
    }
    return txt_2_img(params)


def txt_2_img(params):
    global base_repo_id_data
    global pytorch_device
    global is_test_mode
    global on_progress
    global on_cooling_down
    global cooling_down_deadline_timestamp
    global cancelling_flag
    global on_progress_session_id
    global last_session_id
    global current_generating_user_id
    global current_generating_user_comes_from
    global used_seed
    global base64_data
    global cooling_down_count_down
    global cooling_down_duration
    global next_image_data_name
    global is_same_user
    global generating_base_index
    global generating_base_steps
    global generating_refiner_index
    global generating_refiner_steps

    json_response = {}
    last_session_id = None
    seed = params['seed']
    try:

        g = torch.Generator(device=get_device_name())
        if seed is not None:
            # print('=====seed=====')
            # print(seed)
            seed = int(seed)
            g.manual_seed(seed)
        else:
            seed = g.seed()

        if on_progress is True:
            return json_response_ensure_ascii({
                'result': 'success',
                'code': 10001,
                'message': '有任务在执行'
            })
        else:
            on_progress_session_id = params['session_id']

            current_generating_user_comes_from = params.get(
                'current_generating_user_comes_from', None)
            current_generating_user_id = params.get('current_generating_user_id', None)

        print('=====txt_2_img=====')
        print('=====current_generating_user_id=====')
        print(current_generating_user_id)

        used_seed = seed
        on_progress = True
        on_cooling_down = False
        # ================================
        # 假装执行
        # ================================
        if is_test_mode is True:
            if current_generating_user_id == 47:
                base64_data = base64_image_data1
            elif current_generating_user_id == 32:
                base64_data = base64_image_data2
            time.sleep(execution_duration)
            json_response = json_response_ensure_ascii({
                'code': 10000,
                'data': base64_data,
                'sessionId': on_progress_session_id,
                'seed': used_seed,
                'userId': current_generating_user_id,
                'userComesFrom': current_generating_user_comes_from,
                'message': '图片生成成功'
            })
        # ================================
        # 实际执行
        # ================================
        else:
            use_refiner = params.get('num_inference_steps_refiner') is not None
            base_repo_id_data = get_repo_id('stable-diffusion-xl-base-1.0')
            base_repo_id = base_repo_id_data.envPath + base_repo_id_data.repoName

            print('=====seed=====')
            print(seed)
            print('=====positive_prompt=====')
            print(params.get('custom_positive_prompt'))
            print('=====num_inference_steps_refiner=====')
            print(params.get('num_inference_steps_refiner'))
            print(langid.classify(params.get('custom_positive_prompt')))
            print(type(langid.classify(params.get('custom_positive_prompt')))[0])
            custom_positive_prompt = params.get('custom_positive_prompt')
            custom_negative_prompt = params.get('custom_negative_prompt')
            if langid.classify(custom_positive_prompt)[0] != 'en':
                translated_prompt = _translator(params.get('custom_positive_prompt'))
                custom_positive_prompt = translated_prompt[0]
            if langid.classify(custom_negative_prompt)[0] != 'en':
                translated_prompt = _translator(params.get('custom_negative_prompt'))
                custom_negative_prompt = translated_prompt[0]

            print('=====_translator(custom_positive_prompt)=====')
            print(custom_positive_prompt)
            print(custom_negative_prompt)

            positive_comma = ','
            if custom_positive_prompt == '' or params.get('positive_prompt') == '':
                positive_comma = ''
            assembled_positive_prompt = params.get(
                'positive_prompt') + positive_comma + custom_positive_prompt

            negative_comma = ','
            if custom_negative_prompt == '' or params.get('negative_prompt') == '':
                negative_comma = ''
            assembled_negative_prompt = params.get(
                'negative_prompt') + negative_comma + custom_negative_prompt

            print('=====assembled_positive_prompt=====')
            print(assembled_positive_prompt)
            print('=====assembled_negative_prompt=====')
            print(assembled_negative_prompt)

            high_noise_frac = 0.8
            guidance_scale = 7.5

            if seed is None:
                seed = -1

            gc.collect()
            torch.cuda.empty_cache()
            # torch.backends.cuda.matmul.allow_tf32 = True
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"

            # base_repo_id = './models/stable-diffusion-xl-base-1.0'

            use_cuda_base = base_repo_id_data.useCuda
            settings_data_json = get_settings(base_repo_id_data)
            if base_repo_id is None:
                return json_response_ensure_ascii({
                    "error": 'base_repo_id is None'
                }, status=400)
            # base_repo_id = 'stabilityai/stable-diffusion-xl-base-1.0'
            # refiner_repo_id = 'stabilityai/stable-diffusion-xl-refiner-1.0'
            print('=================')
            print(base_repo_id)
            print("Torch version:", torch.__version__)
            print("Is CUDA available?", torch.cuda.is_available())
            print("Is Base using CUDA?", use_cuda_base)
            print("Is using Refiner??", use_refiner)

            print('=====  if params.useFp32 is True:=====')
            print(params.get('useFp32'))
            if params.get('useFp32') is True:
                base = StableDiffusionXLPipeline.from_pretrained(
                    base_repo_id,
                    local_files_only=True,
                    use_safetensors=True,
                    cache_dir='./models/',
                )
            else:
                base = StableDiffusionXLPipeline.from_pretrained(
                    base_repo_id,
                    local_files_only=True,
                    use_safetensors=True,
                    cache_dir='./models/',
                    variant="fp16",
                    torch_dtype=torch.float16,
                )

            if settings_data_json.get('unet') is True:
                base.unet = torch.compile(base.unet, mode="reduce-overhead",
                                          fullgraph=True)

            # 整个SD模型CPU <-> GPU切换
            if use_cuda_base is True:
                base.to(get_device_name())
            else:
                # 子模块CPU <-> GPU切换
                base.enable_sequential_cpu_offload()

            # 切片注意力
            if params.get('enable_attention_slicing') is True:
                base.enable_attention_slicing()
            # 切片VAE
            if params.get('enable_attention_slicing') is True:
                base.enable_vae_slicing()
            # 大图像切块
            if params.get('enable_attention_slicing') is True:
                base.enable_vae_tiling()
            # 大图像切块
            if params.get('enable_xformers_memory_efficient_attention') is True:
                base.enable_xformers_memory_efficient_attention()

            if params.get('positive_prompt') is None:
                positive_prompt = '8k wallpaper, highly detailed, illustration, 1 girl, long hair, detailed eyes, forrest, hanfu,lakes, soft smile,bamboo,Tea'

            # prompt = "Watercolor painting of a desert landscape, with sand dunes, mountains, and a blazing sun, soft and delicate brushstrokes, warm and vibrant colors"
            # negative_prompt = "(EasyNegative),(watermark), (signature), (sketch by bad-artist), (signature), (worst quality), (low quality), (bad anatomy), NSFW, nude, (normal quality)"

            g = torch.Generator(device=get_device_name())
            if seed != -1:
                g.manual_seed(seed)
            else:
                seed = g.seed()

            used_seed = seed
            print('=====used_seed=====')
            print(used_seed)
            # LCM LoRA
            print('=====useLcmLora=====')
            print(params.get('useLcmLora'))
            if params.get('useLcmLora') is True:
                lcm_lora_adapter_id_data = get_repo_id('lcm-lora-sdxl')
                lcm_lora_adapter_id = base_repo_id_data.envPath + lcm_lora_adapter_id_data.repoName
                base.load_lora_weights(lcm_lora_adapter_id, torch_dtype=torch.float16)
                base.scheduler = LCMScheduler.from_config(base.scheduler.config, torch_dtype=torch.float16)
                guidance_scale = 1.5

            if params.get('sampler') != '':
                base = sampler_checker(params.get('sampler'), base)

            if use_refiner is True:
                refiner_repo_id_data = get_repo_id('stable-diffusion-xl-refiner-1.0')
                refiner_repo_id = refiner_repo_id_data.envPath + refiner_repo_id_data.repoName
                use_cuda_refiner = refiner_repo_id_data.useCuda

                refiner = StableDiffusionXLPipeline.from_pretrained(
                    refiner_repo_id,
                    # text_encoder_2=base.text_encoder_2,
                    # vae=base.vae,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16",
                )

                refiner.to(get_device_name())
                # else:
                # 子模块CPU <-> GPU切换
                # refiner.enable_sequential_cpu_offload()

                # 切片注意力
                # refiner.enable_attention_slicing()
                # 切片VAE
                #         refiner.enable_vae_slicing()
                # 大图像切块
                #         refiner.enable_vae_tiling()
                # refiner.enable_xformers_memory_efficient_attention()
                latent_data = base(
                    prompt=assembled_positive_prompt,
                    negative_prompt=assembled_negative_prompt,
                    width=params.get('width'),
                    height=params.get('height'),
                    guidance_scale=guidance_scale,
                    num_inference_steps=params.get('num_inference_steps'),
                    generator=g,
                    callback_on_step_end=report_base_progress,
                    output_type="latent",
                    # denoising_end=high_noise_frac,
                ).images

                print('=====Begin to use refiner=====')
                print('steps：' + str(params.get('num_inference_steps_refiner')))

                pil_image_data = refiner(
                    prompt=assembled_positive_prompt,
                    negative_prompt=assembled_negative_prompt,
                    num_inference_steps=params.get('num_inference_steps_refiner'),
                    callback_on_step_end=report_refiner_progress,
                    denoising_start=0.8,
                    image=latent_data,
                    # generator=g,
                    # strength=0.3,
                ).images
            else:
                pil_image_data = base(
                    prompt=assembled_positive_prompt,
                    negative_prompt=assembled_negative_prompt,
                    width=params.get('width'),
                    height=params.get('height'),
                    guidance_scale=guidance_scale,
                    num_inference_steps=params.get('num_inference_steps'),
                    generator=g,
                    callback_on_step_end=report_base_progress,
                    # denoising_end=high_noise_frac,
                ).images

            pil_image_data = pil_image_data[0]
            generating_base_index = None
            generating_refiner_index = None
            current_timestep_base = None
            current_timestep_refiner = None
            base64_data = transform_pil_image_to_base64(pil_image_data)
            json_response = json_response_ensure_ascii({
                'code': 10000,
                'data': base64_data,
                'sessionId': on_progress_session_id,
                'seed': used_seed,
                'userId': current_generating_user_id,
                'userComesFrom': current_generating_user_comes_from,
                'message': '图片生成成功'
            })
            gc.collect()
            torch.cuda.empty_cache()
            if base64_data is not None:
                print('Generation successful...')
            temporary_latent_base64 = None
            if platform.system() != 'Darwin':
                print(torch.cuda.memory_summary())

    except Exception as error:
        print('=====txt_2_img_error=====')
        print(error)
        print("Torch version:", torch.__version__)
        print("Is CUDA available?", torch.cuda.is_available())
        generating_base_index = None
        generating_refiner_index = None
        current_timestep_base = None
        current_timestep_refiner = None
        on_progress = False
        temporary_latent_base64 = None
        current_generating_user_id = None
        current_generating_user_comes_from = None

        on_progress = False
        cancelling_flag = False
        on_progress_session_id = None

        json_response = json_response_ensure_ascii({
            "error": error
        }, status=400)
        gc.collect()
        torch.cuda.empty_cache()
    finally:
        print('finally!!!!!!!!!!!!!!!!!!!!!!!!!1')

    if cancelling_flag is True:
        json_response = json_response_ensure_ascii({
            'code': 10002,
            'sessionId': on_progress_session_id,
            'userId': current_generating_user_id,
            'userComesFrom': current_generating_user_comes_from,
            'message': '生成任务取消'
        })

    on_progress = False
    cancelling_flag = False
    last_session_id = on_progress_session_id
    on_progress_session_id = None
    on_cooling_down = True
    is_same_user = None
    generating_base_index = None
    generating_base_steps = None
    generating_refiner_index = None
    generating_refiner_steps = None
    current_generating_user_id = None
    current_generating_user_comes_from = None
    cooling_down_deadline_timestamp = 0
    cooling_down_deadline_timestamp = cooling_down_duration + time.time()
    return json_response


def check_cooling_down():
    global cooling_down_deadline_timestamp
    global cooling_down_count_down
    global on_cooling_down

    if cooling_down_deadline_timestamp is not None:
        cooling_down_count_down = cooling_down_deadline_timestamp - time.time()
        if cooling_down_count_down < 0:
            cooling_down_deadline_timestamp = None
            cooling_down_count_down = None
            on_cooling_down = False


def get_generation_status(request):
    global on_progress
    global cancelling_flag
    global cooling_down_deadline_timestamp
    global cooling_down_count_down
    global generating_base_index
    global generating_base_steps
    global generating_refiner_index
    global generating_refiner_steps
    global temporary_latent_base64
    global current_timestep_base
    global current_timestep_refiner
    global current_generating_user_id
    global on_cooling_down
    global is_same_user

    check_cooling_down()

    request_json = json.loads(request.body)
    app_user_id = request_json.get('appUserId')
    user_id = request_json.get('userId')

    _generating_base_steps = None
    _generating_refiner_steps = None
    if generating_base_steps is not None:
        _generating_base_steps = len(generating_base_steps)
    if generating_refiner_steps is not None:
        _generating_refiner_steps = len(generating_refiner_steps)

    # print('=====current_generating_user_id=====')
    # print(current_generating_user_id)
    # print(user_id)
    # print(user_id == current_generating_user_id)

    if on_progress is True or cancelling_flag is True or on_cooling_down is True:
        is_same_user = user_id == current_generating_user_id
    else:
        is_same_user = None

    if is_same_user is True or is_same_user is None:
        result = {
            'sessionId': on_progress_session_id,
            'onCancelling': cancelling_flag,
            'onProgress': on_progress,
            'onCoolingDown': on_cooling_down,
            'coolingDownCountDown': cooling_down_count_down,
            'generatingIndexBase': generating_base_index,
            'currentTimestepBase': current_timestep_base,
            'generatingIndexRefiner': generating_refiner_index,
            'currentTimestepRefiner': current_timestep_refiner,
            'temporaryLatent': temporary_latent_base64,
            'isSameUser': is_same_user
        }
    else:
        result = {
            'sessionId': on_progress_session_id,
            'onCancelling': cancelling_flag,
            'onProgress': on_progress,
            'onCoolingDown': on_cooling_down,
            'coolingDownCountDown': cooling_down_count_down,
            'isSameUser': False
        }

    response_json = {
        'result': 'success',
    }
    response_json.update(result)

    return json_response_ensure_ascii(response_json)


def get_settings(repo_data):
    print('=====get_settings=====')
    if repo_data.defaultSettings is not None:
        setting_data_json = json.loads(repo_data.defaultSettings)
    return setting_data_json


def get_last_image_data(self):
    global base64_data
    global last_session_id
    global used_seed
    print('=====get_last_image_data=====')
    if base64_data is not None:
        print('base64_data is not None')
        json_response = json_response_ensure_ascii({
            'code': 20000,
            'data': base64_data,
            'seed': used_seed,
            'sessionId': last_session_id
        })
    else:
        print('base64_data is None')
        json_response = json_response_ensure_ascii({
            'code': 20001,
            'sessionId': last_session_id,
            'seed': used_seed,
            'data': None
        })

    return json_response


@torch.no_grad()
def decode_latents(vae, latents, base):
    print('=====decode_latents1=====')
    print(vae.config.scaling_factor)
    latents = latents / vae.scaling_factor
    print(latents[0])
    with torch.no_grad():
        image = vae.decode(latents).sample[0]
    print('=====decode_latents2=====')
    print(image)
    image = image.mul(0.5).add(0.5).clamp(0, 1)
    image = image.cpu().permute(1, 2, 0).numpy()
    return base.numpy_to_pil(image)


def report_base_progress(pipe, step_index, timestep, callback_kwargs):
    _vae = pipe.vae
    # vae = AutoencoderTiny.from_pretrained("madebyollin/taesdxl", torch_dtype=dtype)
    global generating_base_index
    # global generating_base_steps
    global current_timestep_base
    global cancelling_flag
    global on_progress
    global initialized_flag
    global temporary_latent_base64
    global base_repo_id_data
    global pytorch_device
    generating_base_index = step_index
    current_timestep_base = int(timestep.cpu().numpy())
    base_repo_id = base_repo_id_data.envPath + base_repo_id_data.repoName

    print('====pipe.vae.scaling_factor====')
    print(_vae.scaling_factor)
    temporary_latent = callback_kwargs.get('latents')[0]
    # print('=====temporary_latent=====')
    # print(callback_kwargs.get('latents'))
    # pil_image = decode_latents(_vae, temporary_latent, pipe)
    # temporary_latent_base64 = transform_pil_image_to_base64(pil_image)

    temporary_latent_base64 = transform_latent_to_base64(temporary_latent)

    if generating_base_index is not None:
        initialized_flag = True

    if cancelling_flag is True:
        print('cancelled from base!!!')
        cancelling_flag = False
        on_progress = False
        generating_base_index = None

        gc.collect()
        torch.cuda.empty_cache()

        raise Exception("Inference cancelled.")

    return callback_kwargs


def report_refiner_progress(pipe, step_index, timestep, callback_kwargs):
    global generating_refiner_index
    # global generating_refiner_steps
    global cancelling_flag
    global on_progress
    global initialized_flag
    global current_timestep_refiner

    print('=====timestep=====')
    print(timestep)
    print(timestep.cpu().numpy())
    print(step_index)

    generating_refiner_index = step_index
    current_timestep_refiner = int(timestep.cpu().numpy())
    # generating_refiner_steps = steps

    if cancelling_flag is True:
        print('cancelled from refiner!!!')
        cancelling_flag = False
        on_progress = False
        generating_refiner_index = None

        gc.collect()
        torch.cuda.empty_cache()

        raise Exception("Inference cancelled.")

    return callback_kwargs


def cancel_generation(self):
    print('=====cancel_generation=====')
    global on_progress_session_id
    global cancelling_flag
    global on_progress
    if cancelling_flag is False and on_progress is True:
        # cancel_generation_sleep_looper()
        print('cancelling_flag = True')
        cancelling_flag = True

    on_progress = False
    # cancelling_flag = False

    return json_response_ensure_ascii({
        'result': 'success',
        'sessionId': on_progress_session_id,
        'data': cancelling_flag
    })


def _cancel_generation(self):
    print('=====cancel_generation=====')
    global cancelling_flag
    if cancelling_flag is False and on_progress is True:
        # cancel_generation_sleep_looper()
        print('cancelling_flag = True')
        cancelling_flag = True

    return json_response_ensure_ascii({
        'result': 'success',
        'sessionId': on_progress_session_id,
        'data': cancelling_flag
    })


def cancel_generation_sleep_looper():
    global generating_base_index
    global generating_base_steps
    global cancelling_flag

    print('canceling')
    print('cancelling_flag=' + str(cancelling_flag))
    if cancelling_flag is False:
        print('=====cancel_generation_sleep_looper1=====')
        print('cancelled!!!')
        return {
            'result': 'success',
            'data': 'cancelled'
        }

    else:
        time.sleep(3)
        cancel_generation_sleep_looper()


sleep_flag = True


def get_cancelling_progress(self):
    global cancelling_flag
    return json_response_ensure_ascii({
        'result': 'success',
        'status': cancelling_flag,
        'sessionId': on_progress_session_id
    })


def handle_check_queue_by_user_id(request):
    request_bytes = request.body
    request_json = json.loads(request_bytes)
    user_id = request_json.get('userId')
    queue_info = check_queue(user_id)
    return json_response_ensure_ascii({
        "message": queue_info.get('message'),
        'code': queue_info.get('code'),
        "data": queue_info.get('data'),
        "onProgressSessionId": queue_info.get('on_progress_session_id'),
    })


def check_queue(user_id):
    global on_progress_session_id
    Session = sessionmaker(bind=engine)
    session = Session()
    data = session.query(Queue)
    all_data = data
    user_data = data.filter_by(userId=user_id)

    all_data_length = len(all_data.all())
    user_data_length = len(user_data.all())

    all_data_list = []
    if all_data_length > 0:
        for item in all_data:
            all_data_list.append(item.to_json())

    user_data_list = []
    if user_data_length > 0:
        for item in user_data:
            user_data_list.append(item.to_json())

    print('=====user_data=====')
    print(user_data)

    message = None
    code = None
    data = None
    result = []

    if all_data_length == 0:
        message = '整体队列为空'
        code = 10000

    elif user_data_length == 0:
        message = '本用户队列为空'
        code = 10001

    elif user_data_length > 0:
        print('on_progress_session_id+++++', on_progress_session_id)
        for item in user_data_list:
            result.append({
                'data': item,
                'active': item['sessionId'] == on_progress_session_id
            })

        message = '本用户队列有待执行任务'
        code = 10002
        data = result

    return {
        'message': message,
        'code': code,
        'data': data,
        'onProgressSessionId': on_progress_session_id,
    }


def delete_queue(request):
    request_bytes = request.body
    request_json = json.loads(request_bytes)
    session_id_list = request_json.get('sessionId')
    Session = sessionmaker(bind=engine)
    session = Session()
    for item in session_id_list:
        data = session.query(Queue).filter_by(sessionId=item)
        data.delete()
    session.commit()
    session.close()

    if len(session_id_list) > 0:
        message = '删除session成功'
        code = 10000
    else:
        message = '无现存session'
        code = 10001

    return json_response_ensure_ascii({
        "result": 'Successful',
        "data": session_id_list,
        "message": message,
        'code': code
    })


def transform_latent_to_pil_image(latent_data):
    pil_image = transforms.ToPILImage()(latent_data).convert('RGB')
    return pil_image


def transform_latent_to_base64(latent_data):
    pil_image = transform_latent_to_pil_image(latent_data)
    # Encode the bytes to base64
    base64_string = transform_pil_image_to_base64(pil_image)
    return base64_string


def transform_pil_image_to_base64(pil_image_data):
    buffered = BytesIO()
    pil_image_data.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    image_b64 = (f"data:image/jpeg;base64,{img_str}")

    response_data = image_b64

    return response_data


def handle_add_queue(request):
    request_bytes = request.body
    request_json = json.loads(request_bytes)

    params = {
        'sessionId': request_json.get('sessionId'),
        'positivePrompt': request_json.get('positivePrompt'),
        'customPositivePrompt': request_json.get('customPositivePrompt'),
        'negativePrompt': request_json.get('negativePrompt'),
        'customNegativePrompt': request_json.get('customNegativePrompt'),
        'numInferenceSteps': request_json.get('numInferenceSteps'),
        'width': request_json.get('width'),
        'height': request_json.get('height'),
        'seed': request_json.get('seed'),
        'otherSettings': request_json.get('otherSettings'),

        'welinkUserId': request_json.get('welinkUserId'),
        'guestUserId': request_json.get('guestUserId'),
        'userId': request_json.get('userId'),
        'userComesFrom': request_json.get('userComesFrom'),

        'lifeCycle': 'awaiting'
    }
    return add_queue(params)


def add_queue(params):
    Session = sessionmaker(bind=engine)
    session = Session()
    otherSettings = json.dumps(params['otherSettings'])
    print('=====add_queue=====')
    print(params)
    exist_data_by_user_json = []

    # exist_data = session.query(Queue).filter_by(userId=params['userId']).all()
    session.add(
        Queue(
            sessionId=params['sessionId'],
            positivePrompt=params['positivePrompt'],
            customPositivePrompt=params['customPositivePrompt'],
            negativePrompt=params['negativePrompt'],
            customNegativePrompt=params['customNegativePrompt'],
            numInferenceSteps=params['numInferenceSteps'],
            width=params['width'],
            height=params['height'],
            seed=params['seed'],

            otherSettings=otherSettings,

            welinkUserId=params['welinkUserId'],
            guestUserId=params['guestUserId'],
            userId=params['userId'],

            lifeCycle=params['userId'],

            userComesFrom=params['userComesFrom'],
            createdAt=datetime.datetime.now(),
        ))
    message = '队列添加成功'
    code = 10000
    # if len(exist_data) == 0:
    # else:
    #     for item in exist_data:
    #         exist_data_by_user_json.append(item.to_json())
    #     message = '本用户队列中已存在未完成任务'
    #     code = 10001

    exist_data = session.query(Queue).filter_by(userId=params['userId']).all()

    for item in exist_data:
        exist_data_by_user_json.append(item.to_json())

    session.commit()
    session.close()

    return json_response_ensure_ascii({
        'result': 'successful',
        'message': message,
        'existData': exist_data_by_user_json,
        'code': code
    })
