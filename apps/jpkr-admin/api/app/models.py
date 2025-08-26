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
    word_id: str
    word_info: Optional[str] = None
    tags: str
    jp_text: str
    kr_meaning: str
    num_audio: Optional[int] = None
    audio: Optional[List[Dict[str, Any]]] = None

class TextData(BaseModel):
    text: str

class UserData(BaseModel):
    id: str
    email: str
    display_name: str
    picture_url: str
    roles: List[str]