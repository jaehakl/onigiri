from __future__ import annotations

from typing import List
from sqlalchemy import (create_engine, MetaData, func,
    text, Text,DateTime,Integer,ForeignKey,Index,)
from sqlalchemy.orm import (DeclarativeBase,mapped_column,Mapped,relationship,sessionmaker,)
from sqlalchemy.dialects.postgresql import (UUID)
from pgvector.sqlalchemy import Vector

from settings import settings

# ---------------------------------------------------------------------
# Database URL & Engine
# ---------------------------------------------------------------------

DB_URL = settings.db_url
engine = create_engine(DB_URL, future=True, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)

# ---------------------------------------------------------------------
# Naming convention (good for migrations & consistent constraint names)
# ---------------------------------------------------------------------
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


# ---------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------
class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

# ---------------------------------------------------------------------
# Tables (App Layer)
# ---------------------------------------------------------------------

class Word(TimestampMixin, Base):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    lemma_id: Mapped[int] = mapped_column(Integer, nullable=False)
    lemma: Mapped[str] = mapped_column(Text, nullable=False)
    jp_pron: Mapped[str] = mapped_column(Text, nullable=False)
    kr_pron: Mapped[str] = mapped_column(Text, nullable=False)
    kr_mean: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=True)
    word_examples: Mapped[List["WordExample"]] = relationship("WordExample", back_populates="word", cascade="all, delete-orphan")
    user_word_skills: Mapped[List["UserWordSkill"]] = relationship("UserWordSkill", back_populates="word", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User", back_populates="words")
    __table_args__ = (Index("idx_words_lemma_id", "lemma_id"),)

class Example(TimestampMixin, Base):
    __tablename__ = "examples"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    tags: Mapped[str] = mapped_column(Text, nullable=False)
    jp_text: Mapped[str] = mapped_column(Text, nullable=False)
    kr_mean: Mapped[str] = mapped_column(Text, nullable=False)
    en_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=True)
    audio_object_key: Mapped[str] = mapped_column(Text, nullable=True)
    image_object_key: Mapped[str] = mapped_column(Text, nullable=True)
    word_examples: Mapped[List["WordExample"]] = relationship("WordExample", back_populates="example", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User", back_populates="examples")
    __table_args__ = (
        # -------- pgvector 인덱스: HNSW (권장, pgvector>=0.5)
        Index(
            "idx_examples_emb_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        # ---- 만약 IVFFlat을 쓰고 싶다면 위 HNSW 주석 처리하고 아래를 사용하세요
        # Index(
        #     "idx_examples_emb_ivf",
        #     "embedding",
        #     postgresql_using="ivfflat",
        #     postgresql_ops={"embedding": "vector_cosine_ops"},
        #     postgresql_with={"lists": 100},  # 데이터 크기에 맞춰 튜닝
        # ),
    )

class WordExample(TimestampMixin, Base):
    __tablename__ = "word_examples"
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey("words.id", ondelete="CASCADE"), primary_key=True)
    example_id: Mapped[int] = mapped_column(Integer, ForeignKey("examples.id", ondelete="CASCADE"), primary_key=True)
    word: Mapped["Word"] = relationship("Word", back_populates="word_examples", lazy="selectin")
    example: Mapped["Example"] = relationship("Example", back_populates="word_examples", lazy="selectin")
    __table_args__ = (
        # PK(word_id, example_id)는 word_id 쪽 탐색은 커버합니다.
        # 역방향(example_id -> word_id) 탐색 최적화를 위해 별도 인덱스 추가
        Index("idx_word_examples_example", "example_id"),
    )
    
class UserWordSkill(TimestampMixin, Base):
    __tablename__ = "user_word_skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    word_id: Mapped[int] = mapped_column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False)
    reading: Mapped[int] = mapped_column(Integer, default=0)
    listening: Mapped[int] = mapped_column(Integer, default=0)
    speaking: Mapped[int] = mapped_column(Integer, default=0)
    word: Mapped["Word"] = relationship("Word", back_populates="user_word_skills")
    user: Mapped["User"] = relationship("User", back_populates="user_word_skills")
    __table_args__ = (
        Index("idx_uws_user_word", "user_id", "word_id"),
        Index("idx_uws_user_updated", "user_id", "updated_at"),
        # UniqueConstraint("user_id", "word_id", name="uq_uws_user_word"),  # 원하면 중복 방지
    )

class UserText(TimestampMixin, Base):
    __tablename__ = "user_texts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Vector] = mapped_column(Vector(768), nullable=True)
    youtube_url: Mapped[str] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str] = mapped_column(Text, nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="user_texts")
