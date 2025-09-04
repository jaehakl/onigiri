from sqlalchemy.orm import Session, selectinload
from sqlalchemy import text, select

from db import Example
from utils.aws_s3 import presign_get_url

def get_similar_examples(example_id: int, db: Session, user_id: str):
    result = db.execute(
        select(Example)
        .where(Example.id == example_id)
    )
    example = result.scalar_one_or_none()
    
    if example is None:
        return {"error": "Example not found"}

    similar_examples = []
    if example.embedding is not None:
        sql = text("""
        SELECT d2.id,
               (d2.embedding <=> d1.embedding) AS cosine_distance
        FROM examples d1
        JOIN examples d2 ON d2.id != d1.id
        WHERE d1.id = :example_id
            AND d1.embedding IS NOT NULL
            AND d2.embedding IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT 10
        """)

        result = db.execute(sql, {"example_id": example_id})
        rows = result.fetchall()

        example_ids = [row.id for row in rows]
        result = db.execute(
            select(Example)
            .where(Example.id.in_(example_ids))
        )
        rows = result.scalars().all()

        similar_examples = []
        for i, row in enumerate(rows):
            similar_examples.append({
                'id': row.id,
                'jp_text': row.jp_text,
                'kr_mean': row.kr_mean,
                'tags': row.tags,
                'audio_url': presign_get_url(row.audio_object_key, expires=600) if row.audio_object_key is not None else None,
                'image_url': presign_get_url(row.image_object_key, expires=600) if row.image_object_key is not None else None,
                'has_embedding': 1 if row.embedding is not None else 0
            })
        
    rv = {
        'example':{
            'id': example.id,
            'jp_text': example.jp_text,
            'kr_mean': example.kr_mean,
            'tags': example.tags,
            'num_words': len(example.word_examples),
            'audio_url': presign_get_url(example.audio_object_key, expires=600) if example.audio_object_key is not None else None,
            'image_url': presign_get_url(example.image_object_key, expires=600) if example.image_object_key is not None else None,
            'has_embedding': 1 if example.embedding is not None else 0
        },
        'similar_examples': similar_examples
    }
    return rv