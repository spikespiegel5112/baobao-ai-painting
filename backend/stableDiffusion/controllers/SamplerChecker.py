from torch import torch
from diffusers import DPMSolverMultistepScheduler, EulerDiscreteScheduler, EulerAncestralDiscreteScheduler


def sampler_checker(sampler_name, pipeline):
    print('========sample_checker========')
    print(sampler_name)

    if sampler_name is 'DPM++ 2M':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'DPM++ 2M Karras':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM++ 2M SDE':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config, algorithm_type="sde-dpmsolver++"
        )
    elif sampler_name is 'DPM++ 2M SDE Karras':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config, use_karras_sigmas=True, algorithm_type="sde-dpmsolver++"
        )
    elif sampler_name is 'DPM++ 2S a':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            pipeline.scheduler.config, use_karras_sigmas=True
        )
    elif sampler_name is 'DPM++ 2S a Karras':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM++ SDE':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM++ SDE Karras':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM2':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM2 Karras':
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config, use_karras_sigmas=True)
    elif sampler_name is 'DPM2 a':
        pipeline.scheduler = EulerDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'DPM2 a Karras':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'DPM adaptive':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'DPM fast':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'Euler':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'Euler a':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'Heun':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'LMS':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
    elif sampler_name is 'LMS Karras':
        pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)

    return pipeline
