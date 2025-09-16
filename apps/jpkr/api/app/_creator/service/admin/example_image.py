import uuid, random
from io import BytesIO
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from _creator.service.generate.stable_diffusion import generate_images_multi_gpu_async
from _creator.settings import settings
from db import Example
from utils.aws_s3 import upload_fileobj, delete_object

async def gen_example_image(
    example_ids: List[int],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()
    inserted_keys = []

    positive_prompt_list = []
    negative_prompt_list = []
    seed_list = []
    for i, example in enumerate(examples):
        positive_prompt_list.append(example.en_prompt)
        negative_prompt_list.append("nsfw, blurry, low quality, bad anatomy, disfigured, deformed, bad hands, missing fingers, "
                                    "extra fingers, worst quality, jpeg artifacts, signature, watermark, text, bad eyes, grotesque, "
                                    "sketchy, logo, rough, incomplete, disgusting, distorted, deformed face, poorly drawn, bad quality")
        seed_list.append(random.randint(0, 2_000_000_000))
    
    try:        
        images, seeds = await generate_images_multi_gpu_async(
            settings.STABLE_DIFFUSION_CKPT,
            positive_prompt_list,
            negative_prompt_list,
            seed_list,
            step=30,
            cfg=9.9,
            height=768,
            width=1024,
            max_chunk_size=4
        )    

        for i, jpg_buf in enumerate(images):
            key = "onigiri/example_image/" + uuid.uuid4().hex + ".jpg"
            byte_buf = BytesIO()
            jpg_buf.save(byte_buf, format="JPEG", quality=85)
            byte_buf.seek(0)
            try:
                upload_fileobj(byte_buf, key, "image/jpeg")
                inserted_keys.append(key)
                if examples[i].image_object_key is not None:
                    delete_object(examples[i].image_object_key)
            except Exception as e:
                print(f"S3 upload failed: {e}")
                continue

            examples[i].image_object_key = key

            if i % 10 == 9:
                db.commit()
                inserted_keys = []
                print(f"Generated image for example {i+1}/{len(examples)}")
        db.commit()
        inserted_keys = []
        print(f"Generated image for example {i+1}/{len(examples)}")
    except Exception as e:
        print(f"Error: {e}")
        for key in inserted_keys:
            try:
                delete_object(key)
            except:
                pass
    return {"message": "Example image generated successfully"}


