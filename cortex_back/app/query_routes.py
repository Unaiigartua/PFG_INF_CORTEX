from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.models import QueryLog
from app.auth.schemas import QueryLogIn
from app.auth.database import get_auth_db
from app.auth.routes import get_current_user

router = APIRouter(prefix="/queries", tags=["queries"])

@router.post("/", response_model=dict)
def log_query(input: QueryLogIn,
              current_user=Depends(get_current_user),
              db: Session = Depends(get_auth_db)):
    entry = QueryLog(user_id=current_user.id, query_text=input.query_text)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "timestamp": entry.timestamp}