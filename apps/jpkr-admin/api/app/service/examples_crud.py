# examples_crud.py
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, select, case
from collections import defaultdict
from typing import List, Dict, Any, Optional
from db import SessionLocal, Example, WordExample, Word
from models import ExampleData

def row_to_dict(obj) -> dict:
    # ORM 객체를 dict로 안전하게 변환
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


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
