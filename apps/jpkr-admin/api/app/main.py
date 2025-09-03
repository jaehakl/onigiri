from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends, Form
from initserver import server
from models import WordData, WordFilterData, ExampleFilterData, ExampleData
from db import SessionLocal
from routers.routes_auth import check_user, get_db
from utils.auth import get_current_user, CurrentUser

# Test Service
from service.get_similar_words import get_similar_words
from service.get_similar_examples import get_similar_examples

# Admin Service
from service.admin.duplicated_words import get_duplicated_words
from service.admin.merge_duplicated_words import merge_duplicated_words
from service.admin.word_embeddings import gen_word_embeddings
from service.admin.example_embeddings import gen_example_embeddings
from service.admin.example_audio import gen_example_audio
from service.admin.example_words import gen_example_words

from service.words_crud import update_words_batch, delete_words_batch
from service.examples_crud import update_examples_batch, delete_examples_batch

from service.admin.filter_words import filter_words_by_criteria
from service.admin.filter_examples import filter_examples_by_criteria

app = server()


# Test API endpoints
@app.get("/test/get-similar-words/{word_id}")
async def api_get_similar_words(request: Request, word_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, get_similar_words, word_id)

@app.get("/test/get-similar-examples/{example_id}")
async def api_get_similar_examples(request: Request, example_id: str, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, get_similar_examples, example_id)

# Admin API endpoints
@app.get("/admin/words/get-duplicated")
async def api_get_duplicated_words(request: Request, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, get_duplicated_words)

@app.post("/admin/words/merge-duplicated")
async def api_merge_duplicated_words(request: Request, word_ids: List[str], new_word_data: WordData, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, merge_duplicated_words, word_ids, new_word_data.model_dump())

# Gen Word, Example Embeddings
@app.post("/admin/words/gen-embeddings")
async def api_gen_word_embeddings(request: Request, word_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, gen_word_embeddings, word_ids)

@app.post("/admin/examples/gen-embeddings")
async def api_gen_example_embeddings(request: Request, example_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, gen_example_embeddings, example_ids)

@app.post("/admin/examples/gen-audio")
async def api_gen_example_audio(request: Request, example_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, gen_example_audio, example_ids)

@app.post("/admin/examples/gen-words")
async def api_gen_example_words(request: Request, example_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, gen_example_words, example_ids)

# Update Word, Example
@app.post("/admin/words/update/batch")
async def api_update_words(request: Request, words_data: List[WordData], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):    
    print(words_data, "words_data")
    return auth_service(request, ["admin"], db, user, update_words_batch, words_data)

@app.post("/admin/examples/update/batch")
async def api_update_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, update_examples_batch, examples_data)

# Delete Word, Example
@app.post("/admin/words/delete/batch")
async def api_delete_words(request: Request, word_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    print(word_ids, "word_ids")
    return auth_service(request, ["admin"], db, user, delete_words_batch, word_ids)

@app.post("/admin/examples/delete/batch")
async def api_delete_examples(request: Request, example_ids: List[str], db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, delete_examples_batch, example_ids)

# Filter Word, Example
@app.post("/admin/words/filter")
async def api_filter_words(request: Request, word_filter_data: WordFilterData, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, filter_words_by_criteria, **word_filter_data.model_dump())

@app.post("/admin/examples/filter")
async def api_filter_examples(request: Request, example_filter_data: ExampleFilterData, db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    return auth_service(request, ["admin"], db, user, filter_examples_by_criteria, **example_filter_data.model_dump())





def auth_service(request: Request, allowed_roles: List[str], db, user, func, *args, **kwargs):    
    if user:
        user_roles = [ur for ur in user.roles]
        user_id = user.id
    else:
        user_roles = []
        user_id = None

    matched_roles = [ur for ur in user_roles if ur in allowed_roles]

    if len(matched_roles) == 0 and '*' not in allowed_roles:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    try:
        return func(*args, **kwargs, db=db, user_id=user_id)
    except Exception as e:
        print("Error: ", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

async def auth_service_async(request: Request, allowed_roles: List[str], db, user, func, *args, **kwargs):    
    if user:
        user_roles = [ur for ur in user.roles]
        user_id = user.id
    else:
        user_roles = []
        user_id = None

    matched_roles = [ur for ur in user_roles if ur in allowed_roles]

    if len(matched_roles) == 0 and '*' not in allowed_roles:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    try:
        return await func(*args, **kwargs, db=db, user_id=user_id)
    except Exception as e:
        print("Error: ", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()