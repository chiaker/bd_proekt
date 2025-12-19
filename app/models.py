from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.types import DECIMAL, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="user")
    categories = relationship("Category", back_populates="user")
    budgets = relationship("Budget", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    balance = Column(DECIMAL(12, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(10), nullable=False)

    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey(
        "accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey(
        "categories.id"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    description = Column(Text)
    transaction_date = Column(Date, default=date.today)

    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey(
        "categories.id"), nullable=False)
    amount_limit = Column(DECIMAL(12, 2), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


class TransactionBA(Base):
    __tablename__ = "transactions_b_a"

    id = Column(Integer, primary_key=True, index=True)
    account_id_from = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    account_id_to = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    description = Column(Text)
    transaction_date = Column(Date, default=date.today)

    account_from = relationship("Account", foreign_keys=[account_id_from])
    account_to = relationship("Account", foreign_keys=[account_id_to])


class Log(Base):
    __tablename__ = "logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    table_name = Column(Text, nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    action_date = Column(DateTime, default=datetime.utcnow)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)