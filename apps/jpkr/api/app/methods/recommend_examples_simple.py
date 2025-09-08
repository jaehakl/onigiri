from datetime import datetime, timezone
from sqlalchemy import func, select, and_
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from db import Example, WordExample, Word, UserWordSkill
from models import ExampleData
from utils.aws_s3 import presign_get_url

def recommend_examples_simple(limit_examples: int = 30, db: Session = None, user_id: str = None) -> List[Example]:
    stmt_ex = select(Example.id, 
                     Example.jp_text, 
                     Example.kr_mean, 
                     Example.en_prompt, 
                     Example.audio_object_key, 
                     Example.image_object_key, 
                     Example.tags
                     ).order_by(func.random()).limit(max(1, limit_examples))
    examples = db.execute(stmt_ex).all()
    examples_result = []
    for row in examples:
        examples_result.append(
            ExampleData(
                id=row.id,
                jp_text=row.jp_text,
                kr_mean=row.kr_mean,
                en_prompt=row.en_prompt,
                audio_url=presign_get_url(row.audio_object_key, expires=600) if row.audio_object_key is not None else None,
                image_url=presign_get_url(row.image_object_key, expires=600) if row.image_object_key is not None else None,
                tags=row.tags,
            )
        )
    examples = examples_result
    return examples