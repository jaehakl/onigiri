from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func
from db import Example, WordExample, Word
from models import ExampleCreate, ExampleUpdate
from utils.words_from_text import extract_words_from_text
from utils.aws_s3 import delete_object

def create_examples_batch(examples_data: List[ExampleCreate], db: Session=None, user_id:str = None):
    words_dict_global = {}
    for example_data in examples_data:
        document, words_dict = extract_words_from_text(example_data.jp_text)
        words_dict_global.update(words_dict)

    words_existing = db.query(Word).filter(Word.lemma_id.in_(list(words_dict_global.keys()))
                                            ).where(Word.user_id == user_id).all()
    words_dict_existing = {w.lemma_id: w.id for w in words_existing}
    for lemma_id, word_data in words_dict_global.items():
        if lemma_id == None:
            continue
        if lemma_id not in words_dict_existing:
            pos = word_data["pos1"]
            level = "N1"
            if pos in ["助詞", "記号", "助動詞","補助記号","接尾辞", "代名詞"]:
                continue
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
            if word_data["lemma_id"] == None:
                continue
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

def update_examples_batch(examples_data: List[ExampleUpdate], db: Session=None, user_id:str = None):
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
    examples = db.query(Example).filter(Example.id.in_(example_ids)).all()
    for example in examples:
        audio_object_key = example.audio_object_key
        image_object_key = example.image_object_key
        if audio_object_key is not None:
            delete_object(audio_object_key)
        if image_object_key is not None:
            delete_object(image_object_key)
    deleted_count = db.query(Example).filter(Example.id.in_(example_ids)).delete(synchronize_session=False)
    db.commit()
    print(f"총 {deleted_count}개의 예문을 일괄 삭제했습니다.")
    return deleted_count
