import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from _creator.service.generate.stable_diffusion import generate_image
from _creator.settings import settings
from db import Example
from utils.aws_s3 import upload_fileobj, delete_object

def gen_example_image(
    example_ids: List[int],
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()
    inserted_keys = []
    try:        
        for i, example in enumerate(examples):
            jpg_buf = generate_image(settings.STABLE_DIFFUSION_CKPT, example.en_prompt)

            key = "onigiri/example_image/" + uuid.uuid4().hex + ".jpg"

            try:
                if example.image_object_key is not None:
                    delete_object(example.image_object_key)
                upload_fileobj(jpg_buf, key, "image/jpeg")
                inserted_keys.append(key)
            except Exception as e:
                print(f"S3 upload failed: {e}")
                continue

            example.image_object_key = key

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


