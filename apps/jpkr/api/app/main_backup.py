from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from initserver import server
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from service.words_crud import create_words_batch, read_words_batch, update_words_batch, delete_words_batch, get_all_words, search_words_by_word
from service.examples_crud import create_examples_batch, read_examples_batch, update_examples_batch, delete_examples_batch, get_all_examples, search_examples_by_text, get_examples_by_word_id
from service.analysis_text import analyze_text
#from service.quiz_records import save_quiz_record, get_quiz_records, get_quiz_statistics

app = server()

# 데이터 모델 정의
class WordData(BaseModel):
    word: str
    jp_pronunciation: str
    kr_pronunciation: str
    kr_meaning: str
    level: str    
    num_examples: str
    examples: List[Dict[str, Any]]

class WordUpdateData(BaseModel):
    word: Optional[str] = None
    jp_pronunciation: Optional[str] = None
    kr_pronunciation: Optional[str] = None
    kr_meaning: Optional[str] = None
    level: Optional[str] = None

class TextAnalysisRequest(BaseModel):
    text: str

class ExampleData(BaseModel):
    word_id: int
    word_info: Optional[str] = None
    tags: Optional[str] = None
    jp_text: str
    kr_meaning: str

class ExampleUpdateData(BaseModel):
    id: Optional[int] = None
    tags: Optional[str] = None
    jp_text: Optional[str] = None
    kr_meaning: Optional[str] = None

class QuizRecordData(BaseModel):
    word_id: int
    type: str
    is_correct: bool
    time_spent: float
    user_answer: str
    correct_answer: str
    timestamp: Optional[str] = None

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

@app.get("/words/random/{count}")
async def get_random_words(count: int = 50):
    try:
        from service.words_crud import get_random_words
        return get_random_words(count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Examples CRUD API endpoints
@app.post("/examples/create/batch")
async def create_examples(examples_data: List[ExampleData]):
    try:
        # Pydantic 모델을 딕셔너리로 변환
        examples_dict = [example.dict() for example in examples_data]
        return create_examples_batch(examples_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/examples/read/batch")
async def read_examples(example_ids: List[int]):
    try:
        return read_examples_batch(example_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/examples/update/batch")
async def update_examples(examples_data: List[ExampleUpdateData]):
    examples_dict = [example.dict(exclude_unset=True) for example in examples_data]
    return update_examples_batch(examples_dict)

@app.post("/examples/delete/batch")
async def delete_examples(example_ids: List[int]):
    try:
        return delete_examples_batch(example_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/examples/all")
async def get_examples(data: Dict[str, Any]):
    limit = data.get("limit")
    offset = data.get("offset")
    print(limit, offset)
    examples = get_all_examples(limit, offset)
    return examples


@app.get("/examples/search/{search_term}")
async def search_example(search_term: str):
    try:
        return search_examples_by_text(search_term)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples/word/{word_id}")
async def get_examples_by_word(word_id: int):
    try:
        return get_examples_by_word_id(word_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Text Analysis API endpoint
@app.post("/text/analyze")
async def analyze_text_endpoint(request: TextAnalysisRequest):
    result = analyze_text(request.text)
    return result

# Quiz Records API endpoints
#@app.post("/quiz/record")
#async def save_quiz_record_endpoint(quiz_record: QuizRecordData):
#    try:
#        result = save_quiz_record(quiz_record.dict())
#        return result
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#
#@app.post("/quiz/records")
#async def get_quiz_records_endpoint(filters: Dict[str, Any] = None):
#    try:
#        result = get_quiz_records(filters)
#        return result
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
#
#@app.post("/quiz/statistics")
#async def get_quiz_statistics_endpoint(filters: Dict[str, Any] = None):
#    try:
#        result = get_quiz_statistics(filters)
#        return result
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))
