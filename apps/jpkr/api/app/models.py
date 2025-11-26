from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, EmailStr


class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"


class LevelEnum(str, Enum):
    N5 = "N5"
    N4 = "N4"
    N3 = "N3"
    N2 = "N2"
    N1 = "N1"


class WordBase(BaseModel):
    lemma: str = Field(..., min_length=1)
    jp_pron: str = Field(..., min_length=1)
    kr_pron: str = Field(..., min_length=1)
    kr_mean: str = Field(..., min_length=1)
    level: LevelEnum


class WordUpdate(WordBase):
    id: int
    lemma_id: Optional[int] = None


class WordOut(WordBase):
    id: int
    lemma_id: Optional[int] = None
    num_examples: Optional[int] = None
    has_embedding: Optional[bool] = None
    examples: Optional[List[Dict[str, Any]]] = None


class ExampleBase(BaseModel):
    tags: str = Field(..., min_length=1)
    jp_text: str = Field(..., min_length=1)
    kr_mean: str = Field(..., min_length=1)
    en_prompt: Optional[str] = None


class ExampleCreate(ExampleBase):
    pass


class ExampleUpdate(ExampleBase):
    id: int


class ExampleOut(ExampleBase):
    id: int
    has_embedding: Optional[bool] = None
    has_audio: Optional[bool] = None
    has_image: Optional[bool] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None


class UserWordSkillData(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    word_id: int
    reading: Optional[int] = Field(None, ge=0)
    listening: Optional[int] = Field(None, ge=0)
    speaking: Optional[int] = Field(None, ge=0)


class TextData(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1)
    text: str = Field(..., min_length=1)
    tags: Optional[str] = None
    youtube_url: Optional[str] = None
    audio_url: Optional[str] = None


class WordFilterData(BaseModel):
    levels: Optional[List[LevelEnum]] = None
    min_examples: Optional[int] = Field(None, ge=0)
    max_examples: Optional[int] = Field(None, ge=0)
    has_embedding: Optional[bool] = None
    limit: Optional[int] = Field(None, ge=1)
    offset: Optional[int] = Field(None, ge=0)


class ExampleFilterData(BaseModel):
    min_words: Optional[int] = Field(None, ge=0)
    max_words: Optional[int] = Field(None, ge=0)
    has_en_prompt: Optional[bool] = None
    has_embedding: Optional[bool] = None
    has_audio: Optional[bool] = None
    has_image: Optional[bool] = None
    limit: Optional[int] = Field(None, ge=1)
    offset: Optional[int] = Field(None, ge=0)


class UserData(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    roles: List[RoleEnum]


# Backwards compatibility alias (legacy name kept for existing service signatures)
WordData = WordUpdate
