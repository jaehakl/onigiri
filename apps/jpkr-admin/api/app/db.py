# db.py
from sqlalchemy import (
    Column, Integer, String, ForeignKey, Date, JSON,
    create_engine, DateTime
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os, sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("ONIGIRI_DB_URL")
if not DB_URL or DB_URL == "":
    DB_URL = "sqlite:///./../../db.sqlite3"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 비동기 엔진 및 세션
#engine = create_async_engine(DB_URL, echo=False)
#AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class Words(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String)
    jp_pronunciation = Column(String)
    kr_pronunciation = Column(String)
    kr_meaning = Column(String)
    level = Column(String)
    #embedding = Column(Vector(768))
    updated_at = Column(DateTime, default=datetime.now)