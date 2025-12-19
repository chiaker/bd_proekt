from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Log
from app.schemas import LogResponse
from app.auth import require_permission, get_current_db_role

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=List[LogResponse])
async def get_logs(
    request: Request,
    table_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить логи. Требуются права на просмотр логов."""
    require_permission(db, request, "logs", "view")
    
    query = db.query(Log)
    
    if table_name:
        query = query.filter(Log.table_name == table_name)
    
    logs = query.order_by(Log.action_date.desc()).limit(limit).all()
    return logs


@router.get("/current-role")
async def get_current_role(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получить текущую роль PostgreSQL пользователя."""
    role = get_current_db_role(db)
    return {"role": role or "неизвестная"}

