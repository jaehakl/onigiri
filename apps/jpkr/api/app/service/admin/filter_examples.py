from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import Example, WordExample

def filter_examples_by_criteria(
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    has_en_prompt: Optional[bool] = None,
    has_embedding: Optional[bool] = None,
    has_audio: Optional[bool] = None,
    has_image: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = None,
    user_id: Optional[str] = None,
):
    # 기본 쿼리 시작
    query = db.query(Example)

    # 단어 수 필터링    
    if min_words is not None or max_words is not None:
        # 서브쿼리로 단어 수 계산
        example_count_subquery = db.query(
            WordExample.example_id,
            func.count(WordExample.word_id).label('word_count')
        ).group_by(WordExample.example_id).subquery()
        
        query = query.outerjoin(
            example_count_subquery,
            Example.id == example_count_subquery.c.example_id
        )
        
        if min_words is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.word_count, 0) >= min_words)
        if max_words is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.word_count, 0) <= max_words)

    if has_en_prompt is not None:
        if has_en_prompt:
            query = query.filter(Example.en_prompt.isnot(None))
        else:
            query = query.filter(Example.en_prompt.is_(None))

    # Embedding 보유 여부 필터링
    if has_embedding is not None:
        if has_embedding:
            query = query.filter(Example.embedding.isnot(None))
        else:
            query = query.filter(Example.embedding.is_(None))

    if has_audio is not None:
        if has_audio:
            query = query.filter(Example.audio_object_key.isnot(None))
        else:
            query = query.filter(Example.audio_object_key.is_(None))

    if has_image is not None:
        if has_image:
            query = query.filter(Example.image_object_key.isnot(None))
        else:
            query = query.filter(Example.image_object_key.is_(None))
    
    
    # 정렬 (생성일 기준 오름차순)
    query = query.order_by(Example.created_at.asc())
    total_count = query.count()
    
    # 페이징
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    
    examples_rv = []
    for example in query.all():
        examples_rv.append({
            'id': example.id,
            'tags': example.tags,
            'jp_text': example.jp_text,
            'kr_mean': example.kr_mean,
            'en_prompt': example.en_prompt,
            'has_embedding': 1 if example.embedding is not None else 0,
            'has_audio': 1 if example.audio_object_key is not None else 0,
            'has_image': 1 if example.image_object_key is not None else 0,
            'created_at': example.created_at,
            'updated_at': example.updated_at,
            'num_words': len(example.word_examples),
        })
    
    return {
        'examples': examples_rv,
        'total_count': total_count
    }