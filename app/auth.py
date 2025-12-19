from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional


def get_current_db_role(db: Session) -> Optional[str]:
    """
    Получает текущую роль PostgreSQL пользователя из подключения к БД.
    """
    try:
        result = db.execute(text("SELECT current_user"))
        role = result.scalar()
        return role
    except Exception:
        return None


def check_permission(db: Session, table_name: str, action: str) -> bool:
    """
    Проверяет права доступа текущей роли PostgreSQL к таблице.
    action: 'view', 'create', 'update', 'delete'
    """
    role = get_current_db_role(db)
    
    if not role:
        return False
    
    # db_admin имеет все права
    if role == "db_admin":
        return True
    
    # app_user имеет права на все действия для всех таблиц (кроме logs - только просмотр)
    if role == "app_user":
        if table_name == "logs":
            return action == "view"
        return action in ["view", "create", "update", "delete"]
    
    # audit_user может только просматривать logs и представления
    if role == "audit_user":
        if table_name == "logs" or table_name in ["user_accounts_summary", "category_transactions_report"]:
            return action == "view"
        return False
    
    # Для других ролей - нет доступа
    return False


def require_permission(db: Session, request: Request, table_name: str, action: str):
    """
    Проверяет права доступа и выбрасывает исключение если доступа нет.
    """
    if not check_permission(db, table_name, action):
        role = get_current_db_role(db) or "неизвестная"
        raise HTTPException(
            status_code=403,
            detail=f"Роль '{role}' не имеет прав для выполнения действия '{action}' на таблице '{table_name}'. Обратитесь к администратору для получения доступа."
        )

