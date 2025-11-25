from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Doc(Base):
    __tablename__ = "docs"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(Text, unique=True, index=True, nullable=False)
    title = Column(Text)
    section = Column(Text)  # Combined breadcrumbs + URL segment
    content = Column(JSONB)  # Normalized structured blocks
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_crawled = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, ForeignKey("docs.doc_id"), index=True, nullable=False)
    type = Column(String, index=True, nullable=False)  # header, paragraph, code_block, list, special_block, etc.
    data = Column(JSONB)  # Entity-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Specification(Base):
    __tablename__ = "specifications"
    
    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text)
    analyst_json = Column(JSONB)
    architect_json = Column(JSONB)
    spec_markdown = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

