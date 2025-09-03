from sqlalchemy.orm import Session
from sqlalchemy import text, select

from db import Word

def get_similar_words(word_id: str, db: Session, user_id: str):
    result = db.execute(
        select(Word)
        .where(Word.id == word_id)
    )
    word = result.scalar_one_or_none()
    
    if word is None:
        return {"error": "Word not found"}

    similar_words = []
    if word.embedding is not None:
        sql = text("""
        SELECT d2.id, d2.word, d2.jp_pronunciation, d2.kr_pronunciation, 
               d2.kr_meaning, d2.level, d2.embedding,
               (d2.embedding <=> d1.embedding) AS cosine_distance
        FROM words d1
        JOIN words d2 ON d2.id != d1.id
        WHERE d1.id = :word_id
            AND d1.embedding IS NOT NULL
            AND d2.embedding IS NOT NULL
        ORDER BY cosine_distance ASC
        LIMIT 10
        """)

        result = db.execute(sql, {"word_id": word_id})
        rows = result.fetchall()
        similar_words = [
                {
                'id': row.id,
                'word': row.word,
                'jp_pronunciation': row.jp_pronunciation,
                'kr_pronunciation': row.kr_pronunciation,
                'kr_meaning': row.kr_meaning,
                'level': row.level,
                'num_examples': 0,  # TODO: 필요시 별도 쿼리로 조회
                'num_images': 0,    # TODO: 필요시 별도 쿼리로 조회
                'has_embedding': 1 if row.embedding is not None else 0
            } for row in rows ]
        
    rv = {
        'word':{
            'id': word.id,
            'word': word.word,
            'jp_pronunciation': word.jp_pronunciation,
            'kr_pronunciation': word.kr_pronunciation,
            'kr_meaning': word.kr_meaning,
            'level': word.level,
            'num_examples': len(word.word_examples),
            'num_images': len(word.images),
            'has_embedding': 1 if word.embedding is not None else 0
        },
        'similar_words': similar_words
    }
    return rv