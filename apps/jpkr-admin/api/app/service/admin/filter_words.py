from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, and_, or_
from db import Word, WordExample


def filter_words_by_criteria(
    levels: Optional[List[str]] = None,
    min_examples: Optional[int] = None,
    max_examples: Optional[int] = None,
    has_embedding: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = None,
    user_id: Optional[str] = None,
):
    """
    Words 테이블에서 다양한 기준으로 필터링하여 단어 목록을 가져옵니다.
    
    Args:
        db: 데이터베이스 세션
        levels: 필터링할 레벨 목록 (예: ['N5', 'N4', 'N3'])
        min_examples: 최소 예문 수
        max_examples: 최대 예문 수
        has_embedding: embedding 보유 여부 (True: 보유, False: 미보유, None: 상관없음)
        limit: 반환할 최대 결과 수
        offset: 건너뛸 결과 수
    
    Returns:
        필터링된 Word 객체 목록
    """
    # 기본 쿼리 시작
    query = db.query(Word)    
    
    # 레벨 필터링
    if levels:
        query = query.filter(Word.level.in_(levels))
    
    # 예문 수 필터링
    
    if min_examples is not None or max_examples is not None:
        # 서브쿼리로 예문 수 계산 (LEFT JOIN 사용)
        example_count_subquery = db.query(
            WordExample.word_id,
            func.count(WordExample.example_id).label('example_count')
        ).group_by(WordExample.word_id).subquery()
        
        query = query.outerjoin(
            example_count_subquery,
            Word.id == example_count_subquery.c.word_id
        )
        
        if min_examples is not None:
            # COALESCE를 사용하여 NULL을 0으로 처리
            query = query.filter(
                func.coalesce(example_count_subquery.c.example_count, 0) >= min_examples
            )
        if max_examples is not None:
            query = query.filter(
                func.coalesce(example_count_subquery.c.example_count, 0) <= max_examples
            )
    
    # Embedding 보유 여부 필터링
    if has_embedding is not None:
        if has_embedding:
            query = query.filter(Word.embedding.isnot(None))
        else:
            query = query.filter(Word.embedding.is_(None))
    
    # 정렬 (생성일 기준 내림차순)
    query = query.order_by(Word.created_at.desc())
    total_count = query.count()
    
    # 페이징
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    
    words_rv = []
    for word in query.all():
        words_rv.append({
            'id': word.id,
            'lemma_id': word.lemma_id,
            'lemma': word.lemma,
            'jp_pron': word.jp_pron,
            'kr_pron': word.kr_pron,
            'kr_mean': word.kr_mean,
            'level': word.level,
            'num_examples': len(word.word_examples),
            'has_embedding': 1 if word.embedding is not None else 0
        })
    
    return {
        'words': words_rv,
        'total_count': total_count
    }