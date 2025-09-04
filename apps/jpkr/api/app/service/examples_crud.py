from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from db import Example, WordExample, Word
from models import ExampleData
from service.analysis.words_from_text import extract_words_from_text

def create_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    words_dict_global = {}
    for example_data in examples_data:
        document, words_dict = extract_words_from_text(example_data.jp_text)
        words_dict_global.update(words_dict)

    words_existing = db.query(Word).filter(Word.lemma_id.in_(list(words_dict_global.keys()))
                                            ).where(Word.user_id == user_id).all()
    words_dict_existing = {w.lemma_id: w.id for w in words_existing}
    for lemma_id, word_data in words_dict_global.items():
        if lemma_id not in words_dict_existing:
            pos = word_data["pos1"]
            level = "N1"
            if pos in ["助詞", "記号", "助動詞","補助記号","接尾辞"]:
                level = "N5"
            new_word = Word(
                user_id=user_id,
                lemma_id=lemma_id,
                lemma=word_data["lemma"],
                jp_pron=word_data["pronBase"],
                kr_pron=word_data["pos1"],
                kr_mean=word_data["type"],
                level=level,
            )
            db.add(new_word)
            db.flush()
            words_dict_existing[lemma_id] = new_word.id
        else:
            pass
    for example_data in examples_data:
        new_example = Example(
            user_id=user_id,
            tags=example_data.tags,
            jp_text=example_data.jp_text,
            kr_mean=example_data.kr_mean,
            en_prompt=example_data.en_prompt,
        )
        db.add(new_example)
        db.flush()  # ID 생성을 위해 flush                
        document, words_dict = extract_words_from_text(example_data.jp_text)
        for word_data in words_dict.values():
            if word_data["lemma_id"] not in words_dict_existing:
                continue
            new_word_example = WordExample(
                word_id=words_dict_existing[word_data["lemma_id"]],
                example_id=new_example.id
            )
            db.add(new_word_example)
            db.flush()
    db.commit()
    return

def update_examples_batch(examples_data: List[ExampleData], db: Session=None, user_id:str = None):
    for example_data in examples_data:
        example = db.query(Example).filter(Example.id == example_data.id).first()            
        if example:
            # 예문 데이터 업데이트
            example.user_id = user_id
            example.tags = example_data.tags
            example.jp_text = example_data.jp_text
            example.kr_mean = example_data.kr_mean
            example.en_prompt = example_data.en_prompt
        else:
            # 해당 ID의 예문이 없는 경우
            raise Exception("Example not found")        
    db.commit()
    return
        
def delete_examples_batch(example_ids: List[int], db: Session=None, user_id:str = None):
    deleted_count = db.query(Example).filter(Example.id.in_(example_ids)).delete(synchronize_session=False)
    db.commit()
    print(f"총 {deleted_count}개의 예문을 일괄 삭제했습니다.")
    return deleted_count                

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
    print(len(query.all()))
    
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