from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from models import UserData
from user_auth.routes import check_user

def auth_service(request: Request, allowed_roles: List[str], db, func, *args, **kwargs):    
    user: UserData = check_user(request, db)
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

async def auth_service_async(request: Request, allowed_roles: List[str], db, func, *args, **kwargs):  
    user: UserData = check_user(request, db)
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