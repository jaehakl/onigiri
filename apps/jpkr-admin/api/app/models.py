from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class WordData(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    word: str
    jp_pronunciation: str
    kr_pronunciation: str
    kr_meaning: str
    level: str   
    num_examples: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None
    num_images: Optional[int] = None
    images: Optional[List[Dict[str, Any]]] = None

class ExampleData(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    tags: str
    jp_text: str
    kr_meaning: str
    num_words: Optional[int] = None
    words: Optional[List[Dict[str, Any]]] = None
    num_audio: Optional[int] = None
    audio: Optional[List[Dict[str, Any]]] = None

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
    min_images: Optional[int] = None
    max_images: Optional[int] = None
    has_embedding: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class ExampleFilterData(BaseModel):
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    min_audios: Optional[int] = None
    max_audios: Optional[int] = None
    has_embedding: Optional[bool] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
