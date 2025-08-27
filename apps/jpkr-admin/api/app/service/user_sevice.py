from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import User


class UserService:
    """사용자와 연관된 모든 데이터를 가져오는 서비스"""
    
    @staticmethod
    def get_users(limit: int, offset: int, db: Session, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        사용자 목록을 가져옵니다.
        """
        try:
            print(offset, limit)
            stmt = select(User)
            if offset is not None:
                stmt = stmt.offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            
            users = db.execute(stmt).scalars().all()
            print(users)
            
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
    def get_user_with_all_data(who: str, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """
        사용자 ID를 받아서 해당 사용자와 연관된 모든 데이터를 가져옵니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID (UUID 문자열)
            
        Returns:
            사용자와 연관된 모든 데이터를 포함한 딕셔너리 또는 None
        """
        if who == "me":
            id_to_get = user_id
        else:
            id_to_get = who

        try:
            # User 테이블을 기준으로 모든 relationship 데이터를 한 번에 가져옴
            # lazy="selectin" 설정으로 인해 JOIN 쿼리가 자동으로 실행됨
            stmt = select(User).where(User.id == id_to_get)
            user = db.execute(stmt).scalar_one_or_none()
            
            if not user:
                return None
            
            # 사용자 데이터를 딕셔너리로 변환
            user_data = {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "email_verified_at": user.email_verified_at,
                    "display_name": user.display_name,
                    "picture_url": user.picture_url,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                },
                "user_roles": [
                    {
                        "role_id": user_role.role_id,
                        "role_name": user_role.role.name if user_role.role else None
                    }
                    for user_role in user.user_roles
                ],
                "words": [
                    {
                        "id": word.id,
                        "root_word_id": word.root_word_id,
                        "word": word.word,
                        "jp_pronunciation": word.jp_pronunciation,
                        "kr_pronunciation": word.kr_pronunciation,
                        "kr_meaning": word.kr_meaning,
                        "level": word.level,
                        "created_at": word.created_at,
                        "updated_at": word.updated_at
                    }
                    for word in user.words
                ],
                "examples": [
                    {
                        "id": example.id,
                        "word_id": example.word_id,
                        "tags": example.tags,
                        "jp_text": example.jp_text,
                        "kr_meaning": example.kr_meaning,
                        "created_at": example.created_at,
                        "updated_at": example.updated_at
                    }
                    for example in user.examples
                ],
                "images": [
                    {
                        "id": image.id,
                        "word_id": image.word_id,
                        "tags": image.tags,
                        "image_url": image.image_url,
                        "created_at": image.created_at,
                        "updated_at": image.updated_at
                    }
                    for image in user.images
                ],
                "user_word_skills": [
                    {
                        "id": skill.id,
                        "word_id": skill.word_id,
                        "skill_kanji": skill.skill_kanji,
                        "skill_word_reading": skill.skill_word_reading,
                        "skill_word_speaking": skill.skill_word_speaking,
                        "skill_sentence_reading": skill.skill_sentence_reading,
                        "skill_sentence_speaking": skill.skill_sentence_speaking,
                        "skill_sentence_listening": skill.skill_sentence_listening,
                        "is_favorite": skill.is_favorite,
                        "created_at": skill.created_at,
                        "updated_at": skill.updated_at
                    }
                    for skill in user.user_word_skills
                ],
                "user_texts": [
                    {
                        "id": text.id,
                        "title": text.title,
                        "text": text.text,
                        "tags": text.tags,
                        "youtube_url": text.youtube_url,
                        "audio_url": text.audio_url,
                        "created_at": text.created_at,
                        "updated_at": text.updated_at
                    }
                    for text in user.user_texts
                ]
            }
            
            return user_data
            
        except Exception as e:
            # 로깅을 위해 예외 정보를 포함
            print(f"Error fetching user data: {str(e)}")
            return None
    
    @staticmethod
    def get_user_summary(who: str, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        if who == "me":
            id_to_get = user_id
        else:
            id_to_get = who
        """
        사용자 ID를 받아서 해당 사용자의 요약 정보만 가져옵니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID (UUID 문자열)
            
        Returns:
            사용자 요약 정보를 포함한 딕셔너리 또는 None
        """
        try:
            stmt = select(User).where(User.id == id_to_get)
            user = db.execute(stmt).scalar_one_or_none()
            
            if not user:
                return None
            
            return {
                "user_id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "stats": {
                    "total_words": len(user.words),
                    "total_examples": len(user.examples),
                    "total_images": len(user.images),
                    "total_texts": len(user.user_texts),
                    "favorite_words": len([skill for skill in user.user_word_skills if skill.is_favorite])
                }
            }
            
        except Exception as e:
            print(f"Error fetching user summary: {str(e)}")
            return None
