from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class WordData(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    lemma_id: Optional[int] = None
    lemma: str
    jp_pron: str
    kr_pron: str
    kr_mean: str
    level: str
    num_examples: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None

class ExampleData(BaseModel):
    id: Optional[int] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    tags: str
    jp_text: str
    kr_mean: str
    en_prompt: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None

class UserData(BaseModel):
    id: str
    email: str
    display_name: str
    picture_url: str
    roles: List[str]

class WordFilterData(BaseModel):
    levels: Optional[List[str]] = None
    min_examples: Optional[int] = None
    max_examples: Optional[int] = None
    has_embedding: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

class ExampleFilterData(BaseModel):
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    has_en_prompt: Optional[bool] = None
    has_embedding: Optional[bool] = None
    has_audio: Optional[bool] = None
    has_image: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None