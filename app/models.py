# app/models.py (ПРАВИЛЬНАЯ ВЕРСИЯ)

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    
    owner = relationship("User", back_populates="courses")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan_name = Column(String)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="subscriptions")