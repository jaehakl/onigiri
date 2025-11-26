from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import TextData
from service.analysis_text import analyze_text
from user_auth.routes import get_db
from user_auth.utils.auth_wrapper import require_roles

router = APIRouter(prefix="/text", tags=["text"])


@router.post("/analyze")
async def api_analyze_text(
    text_data: TextData,
    db: Session = Depends(get_db),
    user=Depends(require_roles(["*"])),
):
    return analyze_text(text_data.text, db=db, user_id=user.id if user else None)
