from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends
from initserver import server
from models import WordData, ExampleData, TextData
from service.words_crud import create_words_batch, update_words_batch, delete_words_batch, get_all_words, search_words_by_word, get_random_words
from service.examples_crud import create_examples_batch, update_examples_batch, delete_examples_batch, get_all_examples, search_examples_by_text, get_examples_by_word_id
from service.analysis_text import analyze_text

from routes_auth import check_user, get_db

app = server()

def admin_only(request: Request, db,  func, *args, **kwargs):
    try:
        user = check_user(request, db)
        if "admin" in user.roles:
            return func(*args, **kwargs, user_id=user.id)
        else:
            print("Forbidden")
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))

def user_only(request: Request, db, func, *args, **kwargs):
    try:
        user = check_user(request, db)
        if "user" in user.roles or "admin" in user.roles:
            return func(*args, **kwargs, user_id=user.id)
        else:
            print("Forbidden")
            raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))

def public_func(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print("Error: ", e)
        raise HTTPException(status_code=500, detail=str(e))



# Words CRUD API endpoints
@app.post("/words/create/batch")
async def api_create_words_batch(request: Request, words_data: List[WordData], db: Session = Depends(get_db)):
    return admin_only(request, db, create_words_batch, words_data)

@app.post("/words/update/batch")
async def api_update_words(request: Request, words_data: List[WordData], db: Session = Depends(get_db)):    
    return admin_only(request, db, update_words_batch, words_data)

@app.post("/words/delete/batch")
async def api_delete_words(request: Request, word_ids: List[str], db: Session = Depends(get_db)):
    return admin_only(request, db, delete_words_batch, word_ids)

@app.post("/words/all")
async def api_get_words(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    limit = data.get("limit")
    offset = data.get("offset")
    return admin_only(request, db, get_all_words, limit, offset)

@app.get("/words/search/{search_term}")
async def api_search_word(request: Request, search_term: str, db: Session = Depends(get_db)):
    return admin_only(request, db, search_words_by_word, search_term)

@app.get("/words/random/{count}")
async def api_get_random_words(request: Request, count: int = 50, db: Session = Depends(get_db)):
    return admin_only(request, db, get_random_words, count)





# Examples CRUD API endpoints
@app.post("/examples/create/batch")
async def api_create_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db)):
    return admin_only(request, db, create_examples_batch, examples_data)

@app.post("/examples/update/batch")
async def api_update_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db)):
    return admin_only(request, db, update_examples_batch, examples_data)

@app.post("/examples/delete/batch")
async def api_delete_examples(request: Request, example_ids: List[str], db: Session = Depends(get_db)):
    return admin_only(request, db, delete_examples_batch, example_ids)

@app.post("/examples/all")
async def api_get_examples(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    limit = data.get("limit")
    offset = data.get("offset")
    return admin_only(request, db, get_all_examples, limit, offset)


@app.get("/examples/search/{search_term}")
async def api_search_example(request: Request, search_term: str, db: Session = Depends(get_db)):
    return admin_only(request, db, search_examples_by_text, search_term)

@app.get("/examples/word/{word_id}")
async def api_get_examples_by_word(request: Request, word_id: str, db: Session = Depends(get_db)):
    return admin_only(request, db, get_examples_by_word_id, word_id)



# Text Analysis API endpoint
@app.post("/text/analyze")
async def api_analyze_text(request: Request, text_data: TextData, db: Session = Depends(get_db)):
    return public_func(analyze_text, text_data.text)
