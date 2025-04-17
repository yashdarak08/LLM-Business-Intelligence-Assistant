# backend/database.py

import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from backend.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    """Database model for ingested documents."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)
    source = Column(String, nullable=True)
    document_type = Column(String, nullable=True)
    ingestion_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    """Database model for document chunks."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    text = Column(Text)
    embedding_vector_id = Column(Integer, nullable=True)  # ID in the FAISS index
    document = relationship("Document", back_populates="chunks")
    
class Query(Base):
    """Database model for tracking user queries."""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float, nullable=True)  # Response time in milliseconds
    retrieved_chunks = relationship("QueryChunk", back_populates="query", cascade="all, delete-orphan")

class QueryChunk(Base):
    """Database model for chunks retrieved for a query."""
    __tablename__ = "query_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"))
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"))
    relevance_score = Column(Float)
    query = relationship("Query", back_populates="retrieved_chunks")

# Create database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise