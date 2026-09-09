from __future__ import annotations
from datetime import datetime
from sqlalchemy import create_engine,String,Float,Integer,Text,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker
import os


class Base(DeclarativeBase):
    pass


class DecisionRecord(Base):
    __tablename__="decisions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
    instrument_id:Mapped[str]=mapped_column(String(128),index=True)
    symbol:Mapped[str]=mapped_column(String(64),index=True)
    action:Mapped[str]=mapped_column(String(32))
    expected_return_pct:Mapped[float|None]=mapped_column(Float,nullable=True)
    confidence:Mapped[float]=mapped_column(Float)
    risk_pct:Mapped[float]=mapped_column(Float)
    payload_json:Mapped[str]=mapped_column(Text)


class EvidenceRecord(Base):
    __tablename__="evidence"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
    instrument_id:Mapped[str|None]=mapped_column(String(128),nullable=True,index=True)
    source_id:Mapped[str]=mapped_column(String(128),index=True)
    source_tier:Mapped[int]=mapped_column(Integer)
    topic:Mapped[str]=mapped_column(String(256),index=True)
    text:Mapped[str]=mapped_column(Text)
    source_url:Mapped[str|None]=mapped_column(Text,nullable=True)


class OutcomeRecord(Base):
    __tablename__="outcomes"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
    instrument_id:Mapped[str]=mapped_column(String(128),index=True)
    strategy_version:Mapped[str]=mapped_column(String(128),index=True)
    predicted_return_pct:Mapped[float]=mapped_column(Float)
    realised_return_pct:Mapped[float]=mapped_column(Float)
    confidence:Mapped[float]=mapped_column(Float)


def database_url()->str:
    return os.getenv("DATABASE_URL","sqlite:///data/global_wealth.db")


def engine():
    url=database_url()
    kwargs={"connect_args":{"check_same_thread":False}} if url.startswith("sqlite") else {}
    return create_engine(url,pool_pre_ping=True,**kwargs)


def init_db():
    eng=engine(); Base.metadata.create_all(eng); return eng


def session_factory():
    return sessionmaker(bind=init_db(),expire_on_commit=False)
