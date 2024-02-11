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


def inpaint(params):
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

    pytorch_device = get_device_name()
    json_response = {}
    last_session_id = None
    seed = params['seed']
    try:
        # 针对Apple silicon芯片
        if platform.system() == 'Darwin':
            g = torch.Generator(device="mps")
        else:
            g = torch.Generator(device="cuda")
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
            # 针对Apple silicon芯片
            if platform.system() == 'Darwin':
                base.to('mps')
            elif use_cuda_base is True:
                base.to('cuda')
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

            # 针对Apple silicon芯片
            if platform.system() == 'Darwin':
                g = torch.Generator(device="mps")
            else:
                g = torch.Generator(device="cuda")
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
                # 针对Apple silicon芯片
                if platform.system() == 'Darwin':
                    refiner.to('mps')
                elif use_cuda_refiner is True:
                    refiner.to('cuda')
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
