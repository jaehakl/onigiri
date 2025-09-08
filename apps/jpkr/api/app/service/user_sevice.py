from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, load_only
from sqlalchemy import select, func
from user_auth.db import User
from db import Word, Example, UserText, UserWordSkill

class UserService:
    """사용자와 연관된 모든 데이터를 가져오는 서비스"""
    
    @staticmethod
    def get_users(limit: int, offset: int, db: Session, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        사용자 목록을 가져옵니다.
        """
        try:
            stmt = select(User)
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            
            users = db.execute(stmt).scalars().all()
            
            return [
                {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                for user in users
            ]
        except Exception as e:
            print(f"Error fetching users: {str(e)}")
            return []
    
    @staticmethod
    def delete_user(id: str, db: Session, user_id: str) -> bool:
        try:
            # 사용자 존재 여부 확인
            user = db.query(User).filter(User.id == id).first()
            if not user:
                print(f"User not found: {id}")
                return False
            
            # 사용자 삭제 (CASCADE 설정으로 인해 연관된 모든 데이터가 자동 삭제됨)
            db.delete(user)
            db.commit()
            
            print(f"User and all related data deleted successfully: {id}")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error deleting user: {str(e)}")
            return False

    def get_user_summary(who: str, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        id_to_get = user_id if who == "me" else who

        # 각 통계값을 상관 서브쿼리로 정의 (fan-out 없이 안전, 1 round-trip)
        total_words = (
            select(func.count(Word.id))
            .where(Word.user_id == User.id)
            .correlate(User)
            .scalar_subquery()
        )
        total_examples = (
            select(func.count(Example.id))
            .where(Example.user_id == User.id)
            .correlate(User)
            .scalar_subquery()
        )
        total_texts = (
            select(func.count(UserText.id))
            .where(UserText.user_id == User.id)
            .correlate(User)
            .scalar_subquery()
        )
        stmt = (
            select(
                User.id,
                User.email,
                User.display_name,
                User.is_active,
                User.created_at,
                total_words.label("total_words"),
                total_examples.label("total_examples"),
                total_texts.label("total_texts"),
            )
            .where(User.id == id_to_get)
            # 불필요한 컬럼 pre-load 방지 (혹시 ORM 객체로 바꿀 때 대비)
            # .options(load_only(User.id, User.email, User.display_name, User.is_active, User.created_at))
        )

        row = db.execute(stmt).first()
        if not row:
            return None

        return {
            "user_id": row.id,
            "email": row.email,
            "display_name": row.display_name,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "stats": {
                "total_words": row.total_words,
                "total_examples": row.total_examples,
                "total_texts": row.total_texts,
            },
        }


    @staticmethod
    def get_user_word_skills(db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        # 1) User 최소 컬럼만 로드 (relationship 로딩 방지)
        user_stmt = (
            select(User.id, User.email, User.display_name, User.is_active, User.created_at, User.updated_at)
            .where(User.id == user_id)
        )
        user_row = db.execute(user_stmt).first()
        if not user_row:
            return None
        # 2) 필요한 컬럼만 JOIN으로 조회 (임베딩 제외)
        skills_stmt = (
            select(
                UserWordSkill.word_id,
                UserWordSkill.reading,
                UserWordSkill.listening,
                UserWordSkill.speaking,
                UserWordSkill.created_at,
                UserWordSkill.updated_at,
                Word.lemma_id,
                Word.lemma,
                Word.jp_pron,
                Word.kr_pron,
                Word.kr_mean,
                Word.level,
            )
            .join(Word, Word.id == UserWordSkill.word_id)
            .where(
                UserWordSkill.user_id == user_row.id,
                UserWordSkill.reading >= 80,
                UserWordSkill.updated_at.isnot(None),
            )
            .order_by(UserWordSkill.updated_at)
        )

        learned_words: Dict[str, List[Dict[str, Any]]] = {"N5": [], "N4": [], "N3": [], "N2": [], "N1": []}
        rows = db.execute(skills_stmt)
        for (
            word_id,
            reading,
            listening,
            speaking,
            skill_created_at,
            skill_updated_at,
            lemma_id,
            lemma,
            jp_pron,
            kr_pron,
            kr_mean,
            level,
        ) in rows:
            if level not in learned_words:
                continue
            learned_words[level].append(
                {
                    "id": word_id,
                    "lemma_id": lemma_id,
                    "lemma": lemma,
                    "jp_pron": jp_pron,
                    "kr_pron": kr_pron,
                    "kr_mean": kr_mean,
                    "level": level,
                    "reading": reading,
                    "listening": listening,
                    "speaking": speaking,
                    "created_at": skill_created_at,
                    "updated_at": skill_updated_at,
                }
            )
        return {
            "user_id": user_row.id,
            "email": user_row.email,
            "display_name": user_row.display_name,
            "is_active": user_row.is_active,
            "created_at": user_row.created_at,
            "updated_at": user_row.updated_at,
            "learned_words": learned_words,
        }