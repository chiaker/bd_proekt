from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class AccountCreate(BaseModel):
    user_id: int
    name: str
    type: str
    balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str
    balance: float
    created_at: datetime


class AccountUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    balance: Optional[float] = None


class CategoryCreate(BaseModel):
    user_id: int
    name: str
    type: str


class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str


class CategoryUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    category_id: int
    amount: float
    description: Optional[str]
    transaction_date: date


class TransactionBACreate(BaseModel):
    account_id_from: int
    account_id_to: int
    amount: float
    description: Optional[str] = None
    transaction_date: Optional[date] = None


class TransactionBAResponse(BaseModel):
    id: int
    account_id_from: int
    account_id_to: int
    amount: float
    description: Optional[str]
    transaction_date: date


class BudgetCreate(BaseModel):
    user_id: int
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount_limit: float
    period_start: date
    period_end: date


class BudgetUpdate(BaseModel):
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    amount_limit: Optional[float] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class LogResponse(BaseModel):
    log_id: int
    table_name: str
    record_id: int
    action: str
    action_date: datetime
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None