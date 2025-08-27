from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends
from initserver import server
from models import WordData, ExampleData, TextData, UserWordSkillData, UserTextData
from service.words_crud import create_words_batch, update_words_batch, delete_words_batch, get_all_words, search_words_by_word
from service.examples_crud import create_examples_batch, update_examples_batch, delete_examples_batch, get_all_examples, search_examples_by_text, get_examples_by_word_id
from service.analysis_text import analyze_text
from service.user_word_skill import create_user_word_skill_batch, update_user_word_skill_batch, delete_user_word_skill_batch, get_user_word_skills_by_word_ids, get_all_user_word_skills
from service.words_personal import create_words_personal, get_random_words_to_learn
from service.user_text_crud import create_user_text, update_user_text, delete_user_text, get_user_text, get_user_text_list
from service.user_sevice import UserService
from db import SessionLocal
from routes_auth import check_user, get_db

app = server()





def auth_service(request: Request, allowed_roles: List[str], db,  func, *args, **kwargs):    
    if '*' in allowed_roles:
        try:
            return func(*args, **kwargs, db=db)
        except Exception as e:
            db.rollback()
            print("Error: ", e)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
    else:
        if db is None:
            db = SessionLocal()

        try:
            user = check_user(request, db)
        except Exception as e:
            print("Error: ", e)
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        try:
            if '*' in allowed_roles:
                return func(*args, **kwargs, db=db)
            else:
                if set(user.roles) & set(allowed_roles):
                    return func(*args, **kwargs, db=db, user_id=user.id)
                else:
                    print("Forbidden")
                    raise HTTPException(status_code=403, detail="Forbidden")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()



# Words CRUD API endpoints
@app.post("/words/create/batch")
async def api_create_words_batch(request: Request, words_data: List[WordData], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, create_words_batch, words_data)

@app.post("/words/update/batch")
async def api_update_words(request: Request, words_data: List[WordData], db: Session = Depends(get_db)):    
    return auth_service(request, ["admin"], db, update_words_batch, words_data)

@app.post("/words/delete/batch")
async def api_delete_words(request: Request, word_ids: List[str], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, delete_words_batch, word_ids)

@app.post("/words/all")
async def api_get_words(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    limit = data.get("limit")
    offset = data.get("offset")
    return auth_service(request, ["*"], db, get_all_words, limit, offset)

@app.get("/words/search/{search_term}")
async def api_search_word(request: Request, search_term: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, search_words_by_word, search_term)

# Words Personal API endpoints
@app.post("/words/create/personal")
async def api_create_words_personal(request: Request, data: List[Dict[str, Any]], db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, create_words_personal, data)

@app.get("/words/personal/random/{limit}")
async def api_get_random_words_to_learn(request: Request, limit: int, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, get_random_words_to_learn, limit)




# Examples CRUD API endpoints
@app.post("/examples/create/batch")
async def api_create_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, create_examples_batch, examples_data)

@app.post("/examples/update/batch")
async def api_update_examples(request: Request, examples_data: List[ExampleData], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, update_examples_batch, examples_data)

@app.post("/examples/delete/batch")
async def api_delete_examples(request: Request, example_ids: List[str], db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, delete_examples_batch, example_ids)

@app.post("/examples/all")
async def api_get_examples(request: Request, data: Dict[str, Any], db: Session = Depends(get_db)):
    limit = data.get("limit")
    offset = data.get("offset")
    return auth_service(request, ["*"], db, get_all_examples, limit, offset)


@app.get("/examples/search/{search_term}")
async def api_search_example(request: Request, search_term: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, search_examples_by_text, search_term)

@app.get("/examples/word/{word_id}")
async def api_get_examples_by_word(request: Request, word_id: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, get_examples_by_word_id, word_id)



# User Text CRUD API endpoints
@app.post("/user_text/create")
async def api_create_user_text(request: Request, user_text_data: UserTextData, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, create_user_text, user_text_data)

@app.get("/user_text/get/{user_text_id}")
async def api_get_user_text(request: Request, user_text_id: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, get_user_text, user_text_id)

@app.get("/user_text/all")
async def api_get_user_text_list(request: Request, limit: int = None, offset: int = None, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, get_user_text_list, limit, offset)

@app.post("/user_text/update")
async def api_update_user_text(request: Request, user_text_data: UserTextData, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, update_user_text, user_text_data)

@app.get("/user_text/delete/{user_text_id}")
async def api_delete_user_text(request: Request, user_text_id: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, delete_user_text, user_text_id)


# User CRUD API endpoints
@app.get("/user_admin/get_all_users/{limit}/{offset}")
async def api_get_user_list(request: Request, limit: int = None, offset: int = None, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, UserService.get_users, limit, offset)

@app.get("/user_data/summary/admin/{user_id}")
async def api_get_user_summary_admin(request: Request, user_id: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, UserService.get_user_summary, user_id)

@app.get("/user_data/all/admin/{user_id}")
async def api_get_user_all_data_admin(request: Request, user_id: str, db: Session = Depends(get_db)):
    return auth_service(request, ["admin"], db, UserService.get_user_with_all_data, user_id)

@app.get("/user_data/summary/user")
async def api_get_user_summary_user(request: Request, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, UserService.get_user_summary, "me")

@app.get("/user_data/all/user")
async def api_get_user_all_data_user(request: Request, db: Session = Depends(get_db)):
    return auth_service(request, ["admin", "user"], db, UserService.get_user_with_all_data, "me")


# Text Analysis API endpoint
@app.post("/text/analyze")
async def api_analyze_text(request: Request, text_data: TextData, db: Session = Depends(get_db)):
    return auth_service(request, ["*"], db, analyze_text, text_data.text)



