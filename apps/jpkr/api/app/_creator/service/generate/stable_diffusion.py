import random
from io import BytesIO
import torch
from diffusers import StableDiffusionXLPipeline

def generate_image(ckpt_path: str, prompt: str, seed: int=None):
    if not hasattr(generate_image, "pipe"):
        generate_image.pipe = StableDiffusionXLPipeline.from_single_file(
            ckpt_path,
            torch_dtype=torch.float16,      # 메모리 여유 없으면 fp16 권장
            use_safetensors=True,
        #    device_map="auto",              # 전체 .to("cuda") 하지 마세요 (오프로딩 유지)
        )
        generate_image.pipe.to("cuda")

        # 메모리 절약 옵션
        generate_image.pipe.enable_attention_slicing()
        generate_image.pipe.enable_vae_slicing()
        #pipe.enable_sequential_cpu_offload()

    if seed is None:
        seed = random.randint(0, 1000000)

    img = generate_image.pipe(
        prompt,
        negative_prompt="nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name",
        num_inference_steps=30,         # SDXL은 28~40 스텝부터 무난
        guidance_scale=5.5,             # 4.5~7.5 구간에서 취향 조절
        height=768, width=1024,        # 기본 1024^2
        generator=torch.Generator(device="cuda").manual_seed(seed),
    ).images[0]

    buf = BytesIO()
    #img.save(f"{prompt.split(',')[0]}_{seed}.jpg", format="JPEG", quality=85)
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf