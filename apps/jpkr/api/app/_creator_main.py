from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends, Form
from user_auth.routes import check_user, get_db

# Test Service
from _creator.service.get_similar_words import get_similar_words
from _creator.service.get_similar_examples import get_similar_examples

# Admin Service
from _creator.service.admin.duplicated_words import get_duplicated_words
from _creator.service.admin.merge_duplicated_words import merge_duplicated_words
from _creator.service.admin.word_embeddings import gen_word_embeddings
from _creator.service.admin.example_embeddings import gen_example_embeddings
from _creator.service.admin.example_audio import gen_example_audio
from _creator.service.admin.example_image import gen_example_image
from _creator.service.admin.example_words import gen_example_words

from service.admin.words_crud import update_words_batch, delete_words_batch
from service.admin.examples_crud import update_examples_batch, delete_examples_batch
from service.admin.filter_words import filter_words_by_criteria
from service.admin.filter_examples import filter_examples_by_criteria

from _creator.settings import settings
from _creator.initserver import server
from _creator.models import WordData, WordFilterData, ExampleFilterData, ExampleData, UserData

app = server()


# Test API endpoints
@app.get("/test/get-similar-words/{word_id}")
async def api_get_similar_words(request: Request, word_id: int, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, get_similar_words, word_id)

@app.get("/test/get-similar-examples/{example_id}")
async def api_get_similar_examples(request: Request, example_id: int, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, get_similar_examples, example_id)

# Admin API endpoints
@app.get("/admin/words/get-duplicated")
async def api_get_duplicated_words(request: Request, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, get_duplicated_words)

@app.post("/admin/words/merge-duplicated")
async def api_merge_duplicated_words(request: Request, word_ids: List[int], new_word_data: WordData, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, merge_duplicated_words, word_ids, new_word_data.model_dump())

# Gen Word, Example Embeddings
@app.post("/admin/words/gen-embeddings")
async def api_gen_word_embeddings(request: Request, word_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, gen_word_embeddings, word_ids)

@app.post("/admin/examples/gen-embeddings")
async def api_gen_example_embeddings(request: Request, example_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, gen_example_embeddings, example_ids)

@app.post("/admin/examples/gen-audio")
async def api_gen_example_audio(request: Request, example_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, gen_example_audio, example_ids)

@app.post("/admin/examples/gen-image")
async def api_gen_example_image(request: Request, example_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, gen_example_image, example_ids)

@app.post("/admin/examples/gen-words")
async def api_gen_example_words(request: Request, example_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, gen_example_words, example_ids)


# Update Word, Example
@app.post("/admin/words/update/batch")
async def api_update_words(request: Request, words_data: List[WordData], db: Session = Depends(get_db)):    
    return auth_service(request, ["admin"], db, update_words_batch, words_data)

@app.post("/admin/examples/update/batch")
async def api_update_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, update_examples_batch, examples_data)

# Delete Word, Example
@app.post("/admin/words/delete/batch")
async def api_delete_words(request: Request, word_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, delete_words_batch, word_ids)

@app.post("/admin/examples/delete/batch")
async def api_delete_examples(request: Request, example_ids: List[int], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, delete_examples_batch, example_ids)

# Filter Word, Example
@app.post("/admin/words/filter")
async def api_filter_words(request: Request, word_filter_data: WordFilterData, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, filter_words_by_criteria, **word_filter_data.model_dump())

@app.post("/admin/examples/filter")
async def api_filter_examples(request: Request, example_filter_data: ExampleFilterData, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, filter_examples_by_criteria, **example_filter_data.model_dump())





def auth_service(request: Request, allowed_roles: List[str], db, func, *args, **kwargs):    
    user_id = settings.ADMIN_USER_ID
    try:
        return func(*args, **kwargs, db=db, user_id=user_id)
    except Exception as e:
        print("Error: ", e)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

