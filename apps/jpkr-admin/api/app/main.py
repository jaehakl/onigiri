from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from initserver import server
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from service.words_crud import create_words_batch, read_words_batch, update_words_batch, delete_words_batch, get_all_words, search_words_by_word

# Add this import for the actor service

#from service.github_service import GitHubService, get_files_from_public_repo, get_file_content_from_public_repo

app = server()

# 데이터 모델 정의
class WordData(BaseModel):
    word: str
    jp_pronunciation: str
    kr_pronunciation: str
    kr_meaning: str
    level: str

class WordUpdateData(BaseModel):
    word: Optional[str] = None
    jp_pronunciation: Optional[str] = None
    kr_pronunciation: Optional[str] = None
    kr_meaning: Optional[str] = None
    level: Optional[str] = None

# Words CRUD API endpoints
@app.post("/words/create/batch")
async def create_words(words_data: List[WordData]):
    try:
        # Pydantic 모델을 딕셔너리로 변환
        words_dict = [word.dict() for word in words_data]
        return create_words_batch(words_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/words/read/batch")
async def read_words(word_ids: List[int]):
    try:
        return read_words_batch(word_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/words/update/batch")
async def update_words(words_data: Dict[int, WordUpdateData]):
    try:
        # Pydantic 모델을 딕셔너리로 변환
        words_dict = {k: v.dict(exclude_unset=True) for k, v in words_data.items()}
        return update_words_batch(words_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/words/delete/batch")
async def delete_words(word_ids: List[int]):
    try:
        return delete_words_batch(word_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/words/all")
async def get_words(data: Dict[str, Any]):
    try:
        limit = data.get("limit")
        offset = data.get("offset")
        words = get_all_words(limit, offset)
        return words
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/words/search/{search_term}")
async def search_word(search_term: str):
    try:
        return search_words_by_word(search_term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))