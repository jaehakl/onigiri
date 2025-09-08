from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
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
    # 필요한 필드만 선택하여 쿼리 최적화 (대용량 필드들 제외)
    query = db.query(
        Example.id,
        Example.tags,
        Example.jp_text,
        Example.kr_mean,
        Example.en_prompt,
        Example.created_at,
        Example.updated_at,
        # 대용량 필드들의 존재 여부만 확인 (실제 값은 가져오지 않음)
        case(
            (Example.embedding.isnot(None), 1),
            else_=0
        ).label('has_embedding'),
        case(
            (Example.audio_object_key.isnot(None), 1),
            else_=0
        ).label('has_audio'),
        case(
            (Example.image_object_key.isnot(None), 1),
            else_=0
        ).label('has_image')
    )

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
    
    # 단어 수를 가져오기 위한 별도 쿼리 (필요한 경우에만)
    example_ids = [row.id for row in query.all()]
    word_counts = {}
    if example_ids:
        word_count_query = db.query(
            WordExample.example_id,
            func.count(WordExample.word_id).label('word_count')
        ).filter(WordExample.example_id.in_(example_ids)).group_by(WordExample.example_id)
        
        for row in word_count_query.all():
            word_counts[row.example_id] = row.word_count
    
    # 결과 재구성
    examples_rv = []
    for row in query.all():
        examples_rv.append({
            'id': row.id,
            'tags': row.tags,
            'jp_text': row.jp_text,
            'kr_mean': row.kr_mean,
            'en_prompt': row.en_prompt,
            'has_embedding': row.has_embedding,
            'has_audio': row.has_audio,
            'has_image': row.has_image,
            'created_at': row.created_at,
            'updated_at': row.updated_at,
            'num_words': word_counts.get(row.id, 0),
        })
    
    return {
        'examples': examples_rv,
        'total_count': total_count
    }