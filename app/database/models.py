from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, ARRAY
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
    normalized_path = Column(Text, unique=True, index=True, nullable=True)  # Normalized path for navigation
    outgoing_links = Column(ARRAY(Text), nullable=True)  # Array of normalized paths this document links to
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


class CrawlerState(Base):
    __tablename__ = "crawler_state"
    
    id = Column(Integer, primary_key=True, index=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    pages_total = Column(Integer, default=0)
    pages_processed = Column(Integer, default=0)
    status = Column(String, default="idle")  # running/idle/error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Run(Base):
    __tablename__ = "runs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = Column(String, nullable=True)  # Telegram user_id
    input_text = Column(Text)
    as_is = Column(JSONB, nullable=True)
    architecture = Column(JSONB, nullable=True)
    scope = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

