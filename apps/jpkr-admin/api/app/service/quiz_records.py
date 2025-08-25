from db import get_db_connection
from datetime import datetime
from typing import Dict, List, Any

def save_quiz_record(quiz_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    퀴즈 기록을 데이터베이스에 저장합니다.
    
    Args:
        quiz_record: 퀴즈 기록 데이터
            - word_id: 단어 ID
            - type: 퀴즈 유형
            - is_correct: 정답 여부
            - time_spent: 소요 시간 (초)
            - user_answer: 사용자 답변
            - correct_answer: 정답
            - timestamp: 타임스탬프
    
    Returns:
        저장된 퀴즈 기록 정보
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 퀴즈 기록 테이블이 없으면 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                quiz_type TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                time_spent REAL NOT NULL,
                user_answer TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words (id)
            )
        """)
        
        # 퀴즈 기록 저장
        cursor.execute("""
            INSERT INTO quiz_records 
            (word_id, quiz_type, is_correct, time_spent, user_answer, correct_answer, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz_record['word_id'],
            quiz_record['type'],
            quiz_record['is_correct'],
            quiz_record['time_spent'],
            quiz_record['user_answer'],
            quiz_record['correct_answer'],
            quiz_record.get('timestamp', datetime.now().isoformat())
        ))
        
        record_id = cursor.lastrowid
        conn.commit()
        
        return {
            'id': record_id,
            'word_id': quiz_record['word_id'],
            'type': quiz_record['type'],
            'is_correct': quiz_record['is_correct'],
            'time_spent': quiz_record['time_spent'],
            'user_answer': quiz_record['user_answer'],
            'correct_answer': quiz_record['correct_answer'],
            'timestamp': quiz_record.get('timestamp', datetime.now().isoformat())
        }
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_quiz_records(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    퀴즈 기록을 조회합니다.
    
    Args:
        filters: 필터 조건
            - word_id: 특정 단어 ID
            - quiz_type: 특정 퀴즈 유형
            - is_correct: 정답 여부
            - start_date: 시작 날짜
            - end_date: 종료 날짜
            - limit: 조회 개수 제한
            - offset: 오프셋
    
    Returns:
        퀴즈 기록 목록
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 기본 쿼리
        query = """
            SELECT 
                qr.id,
                qr.word_id,
                w.surface as word_surface,
                w.kr_meaning as word_meaning,
                qr.quiz_type,
                qr.is_correct,
                qr.time_spent,
                qr.user_answer,
                qr.correct_answer,
                qr.timestamp
            FROM quiz_records qr
            LEFT JOIN words w ON qr.word_id = w.id
            WHERE 1=1
        """
        
        params = []
        
        # 필터 조건 추가
        if filters:
            if filters.get('word_id'):
                query += " AND qr.word_id = ?"
                params.append(filters['word_id'])
            
            if filters.get('quiz_type'):
                query += " AND qr.quiz_type = ?"
                params.append(filters['quiz_type'])
            
            if filters.get('is_correct') is not None:
                query += " AND qr.is_correct = ?"
                params.append(filters['is_correct'])
            
            if filters.get('start_date'):
                query += " AND qr.timestamp >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                query += " AND qr.timestamp <= ?"
                params.append(filters['end_date'])
        
        # 정렬 (최신순)
        query += " ORDER BY qr.timestamp DESC"
        
        # 제한 조건
        if filters and filters.get('limit'):
            query += " LIMIT ?"
            params.append(filters['limit'])
            
            if filters.get('offset'):
                query += " OFFSET ?"
                params.append(filters['offset'])
        
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 결과를 딕셔너리로 변환
        result = []
        for record in records:
            result.append({
                'id': record[0],
                'word_id': record[1],
                'word_surface': record[2],
                'word_meaning': record[3],
                'quiz_type': record[4],
                'is_correct': record[5],
                'time_spent': record[6],
                'user_answer': record[7],
                'correct_answer': record[8],
                'timestamp': record[9]
            })
        
        return result
        
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()

def get_quiz_statistics(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    퀴즈 통계를 조회합니다.
    
    Args:
        filters: 필터 조건
    
    Returns:
        퀴즈 통계 정보
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 기본 WHERE 조건
        where_clause = "WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('word_id'):
                where_clause += " AND word_id = ?"
                params.append(filters['word_id'])
            
            if filters.get('quiz_type'):
                where_clause += " AND quiz_type = ?"
                params.append(filters['quiz_type'])
            
            if filters.get('start_date'):
                where_clause += " AND timestamp >= ?"
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                where_clause += " AND timestamp <= ?"
                params.append(filters['end_date'])
        
        # 전체 통계
        cursor.execute(f"""
            SELECT 
                COUNT(*) as total_quizzes,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_quizzes,
                AVG(time_spent) as avg_time_spent,
                MIN(time_spent) as min_time_spent,
                MAX(time_spent) as max_time_spent
            FROM quiz_records
            {where_clause}
        """, params)
        
        stats = cursor.fetchone()
        
        # 유형별 통계
        cursor.execute(f"""
            SELECT 
                quiz_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct,
                AVG(time_spent) as avg_time
            FROM quiz_records
            {where_clause}
            GROUP BY quiz_type
        """, params)
        
        type_stats = cursor.fetchall()
        
        return {
            'total_quizzes': stats[0],
            'correct_quizzes': stats[1],
            'accuracy': (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
            'avg_time_spent': stats[2],
            'min_time_spent': stats[3],
            'max_time_spent': stats[4],
            'type_statistics': [
                {
                    'type': row[0],
                    'total': row[1],
                    'correct': row[2],
                    'accuracy': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                    'avg_time': row[3]
                }
                for row in type_stats
            ]
        }
        
    except Exception as e:
        raise e
    finally:
        cursor.close()
        conn.close()
