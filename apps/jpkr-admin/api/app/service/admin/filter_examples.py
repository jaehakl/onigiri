from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, and_, or_
from db import Example, ExampleAudio, WordExample, Word
from utils.aws_s3 import presign_get_url

def filter_examples_by_criteria(
    levels: Optional[List[str]] = None,
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    min_audios: Optional[int] = None,
    max_audios: Optional[int] = None,
    has_embedding: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = None,
    user_id: Optional[str] = None,
):
    """
    Examples 테이블에서 다양한 기준으로 필터링하여 예문 목록을 가져옵니다.
    
    Args:
        db: 데이터베이스 세션
        min_words: 최소 단어 수
        max_words: 최대 단어 수
        min_audios: 최소 음성 수
        max_audios: 최대 음성 수
        has_embedding: embedding 보유 여부 (True: 보유, False: 미보유, None: 상관없음)
        limit: 반환할 최대 결과 수
        offset: 건너뛸 결과 수
    
    Returns:
        필터링된 Example 목록
    """
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


    # 음성 수 필터링    
    if min_audios is not None or max_audios is not None:
        # 서브쿼리로 음성 수 계산
        example_count_subquery = db.query(
            ExampleAudio.example_id,
            func.count(ExampleAudio.id).label('audio_count')
        ).group_by(ExampleAudio.example_id).subquery()
        
        query = query.outerjoin(
            example_count_subquery,
            Example.id == example_count_subquery.c.example_id
        )
        
        if min_audios is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.audio_count, 0) >= min_audios)
        if max_audios is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.audio_count, 0) <= max_audios)
    
    
    # Embedding 보유 여부 필터링
    if has_embedding is not None:
        if has_embedding:
            query = query.filter(Example.embedding.isnot(None))
        else:
            query = query.filter(Example.embedding.is_(None))
    
    # 정렬 (생성일 기준 내림차순)
    query = query.order_by(Example.created_at.desc())
    total_count = query.count()
    
    # 페이징
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    print(len(query.all()))
    
    examples_rv = []
    for example in query.all():
        examples_rv.append({
            'id': example.id,
            'tags': example.tags,
            'jp_text': example.jp_text,
            'kr_meaning': example.kr_meaning,
            'num_words': len(example.word_examples),
            'num_audio': len(example.audio),
            'audio_url': presign_get_url(example.audio[0].audio_url, expires=600) if len(example.audio) > 0 else None,
            'has_embedding': 1 if example.embedding is not None else 0            
        })
    
    return {
        'examples': examples_rv,
        'total_count': total_count
    }