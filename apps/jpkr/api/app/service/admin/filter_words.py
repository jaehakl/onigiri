from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, and_, or_, case
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
    # 필요한 필드만 선택하여 쿼리 최적화 (embedding 제외)
    query = db.query(
        Word.id,
        Word.lemma_id,
        Word.lemma,
        Word.jp_pron,
        Word.kr_pron,
        Word.kr_mean,
        Word.level,
        Word.created_at,
        # embedding 존재 여부만 확인 (실제 값은 가져오지 않음)
        case(
            (Word.embedding.isnot(None), 1),
            else_=0
        ).label('has_embedding')
    )
    
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
    
    # 예문 수를 가져오기 위한 별도 쿼리 (필요한 경우에만)
    word_ids = [row.id for row in query.all()]
    example_counts = {}
    if word_ids:
        example_count_query = db.query(
            WordExample.word_id,
            func.count(WordExample.example_id).label('example_count')
        ).filter(WordExample.word_id.in_(word_ids)).group_by(WordExample.word_id)
        
        for row in example_count_query.all():
            example_counts[row.word_id] = row.example_count
    
    # 결과 재구성
    words_rv = []
    for row in query.all():
        words_rv.append({
            'id': row.id,
            'lemma_id': row.lemma_id,
            'lemma': row.lemma,
            'jp_pron': row.jp_pron,
            'kr_pron': row.kr_pron,
            'kr_mean': row.kr_mean,
            'level': row.level,
            'num_examples': example_counts.get(row.id, 0),
            'has_embedding': row.has_embedding
        })
    
    return {
        'words': words_rv,
        'total_count': total_count
    }