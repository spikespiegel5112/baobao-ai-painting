# from diffusers import StableDiffusionPipeline
import json

from django.http import JsonResponse
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast

from .CommonController import get_repo_id
from .CommonController import json_response_ensure_ascii


# from database import engine
# from stableDiffusion.models.Images import Images


def translator(request):
    request_json = json.loads(request.body)
    source = request_json.get('source')
    result = _translator(source)

    print('=====tokenizer=====')
    print(result)

    return json_response_ensure_ascii({
        'result': 'success',
        'data': result[0]
    })


def _translator(source):
    repo_id_data = get_repo_id('mbart-large-50-many-to-many-mmt')
    repo_id = repo_id_data.envPath + repo_id_data.repoName
    print('=====repo_id=====')
    print(repo_id)
    model = MBartForConditionalGeneration.from_pretrained(
        repo_id)
    tokenizer = MBart50TokenizerFast.from_pretrained(
        repo_id)

    # translate Arabic to English
    tokenizer.src_lang = "zh_CN"
    encoded_ar = tokenizer(source, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded_ar,
        forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"]
    )
    result = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

    return result
