"""
Database module for Avangrid APM Platform
SQLite database with SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup - use path relative to this file for portability
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "avangrid.db")
DATABASE_PATH = os.getenv("DATABASE_PATH", _DEFAULT_DB_PATH)
Base = declarative_base()

class Application(Base):
    """Application entity"""
    __tablename__ = 'applications'

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    safe_name = Column(String)
    is_green = Column(Boolean, default=False)
    subcategory = Column(String)
    quick_win = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questionnaire_answers = relationship("QuestionnaireAnswer", back_populates="application", cascade="all, delete-orphan")
    transcripts = relationship("MeetingTranscript", back_populates="application", cascade="all, delete-orphan")
    transcript_answers = relationship("TranscriptAnswer", back_populates="application", cascade="all, delete-orphan")
    synergy_scores = relationship("SynergyScore", back_populates="application", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="application", cascade="all, delete-orphan")

class QuestionnaireAnswer(Base):
    """Answers from the original questionnaire"""
    __tablename__ = 'questionnaire_answers'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    question_text = Column(Text)
    answer_text = Column(Text)
    score = Column(Integer)
    synergy_block = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="questionnaire_answers")

class MeetingTranscript(Base):
    """Meeting transcripts uploaded by users"""
    __tablename__ = 'meeting_transcripts'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    file_name = Column(String)
    transcript_text = Column(Text)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)

    application = relationship("Application", back_populates="transcripts")
    answers = relationship("TranscriptAnswer", back_populates="transcript", cascade="all, delete-orphan")

class TranscriptAnswer(Base):
    """Answers extracted from transcripts using AI"""
    __tablename__ = 'transcript_answers'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    transcript_id = Column(String, ForeignKey('meeting_transcripts.id'))
    question_text = Column(Text)
    answer_text = Column(Text)
    confidence_score = Column(Float)  # 0.0 to 1.0
    extraction_method = Column(String, default='ai_extraction')
    synergy_block = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="transcript_answers")
    transcript = relationship("MeetingTranscript", back_populates="answers")

class DavidNote(Base):
    """David's detailed meeting notes and insights per application"""
    __tablename__ = 'david_notes'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    question_text = Column(Text)
    answer_text = Column(Text)
    synergy_block = Column(String)
    note_type = Column(String, default='answer')  # 'answer' or 'insight'
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", backref="david_notes")

class SynergyScore(Base):
    """Synergy block scores (manual or AI-suggested)"""
    __tablename__ = 'synergy_scores'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    block_name = Column(String)
    score = Column(Integer)  # 1-5
    suggested_by = Column(String)  # 'manual', 'ai_questionnaire', 'ai_transcript'
    confidence = Column(Float)
    rationale = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)
    approved_by = Column(String)
    approved_at = Column(DateTime)

    application = relationship("Application", back_populates="synergy_scores")

class Insight(Base):
    """AI-generated insights about applications"""
    __tablename__ = 'insights'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'), nullable=True)  # Can be portfolio-wide
    insight_type = Column(String)  # 'integration', 'technology_update', 'consolidation', 'risk', etc.
    title = Column(String)
    description = Column(Text)
    priority = Column(String)  # 'P1', 'P2', 'P3'
    recommendation = Column(String)  # 'EVOLVE', 'INVEST', 'MAINTAIN', 'ELIMINATE'
    supporting_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="insights")

class AppInsight(Base):
    """Enhanced per-application strategic insights"""
    __tablename__ = 'app_insights'

    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'))
    insight_type = Column(String)  # 'capability', 'integration', 'recommendation', 'market_alternative', 'technical_debt', 'user_satisfaction'
    content = Column(Text)
    confidence = Column(String)  # 'high', 'medium', 'low'
    evidence = Column(JSON)  # Supporting quotes from transcripts/questionnaire
    action_items = Column(JSON)  # List of specific action items
    affected_systems = Column(JSON)  # Other apps that might be affected
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)  # Track which model generated this

    application = relationship("Application", backref="app_insights")

class PortfolioInsight(Base):
    """Portfolio-level strategic insights and patterns"""
    __tablename__ = 'portfolio_insights'

    id = Column(String, primary_key=True)
    insight_type = Column(String)  # 'consolidation', 'integration', 'gap', 'priority', 'redundancy', 'quick_win'
    title = Column(String)
    description = Column(Text)
    affected_apps = Column(JSON)  # List of app IDs involved
    priority = Column(String)  # 'P1', 'P2', 'P3'
    estimated_impact = Column(String)  # 'high', 'medium', 'low'
    complexity = Column(String)  # 'high', 'medium', 'low'
    recommended_action = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String)

class CustomWeight(Base):
    """Persisted custom weights for synergy blocks"""
    __tablename__ = 'custom_weights'

    block_name = Column(String, primary_key=True)
    weight = Column(Integer, default=25)
    updated_at = Column(DateTime, default=datetime.utcnow)


class QAHistory(Base):
    """Q&A chat history with AI assistant"""
    __tablename__ = 'qa_history'

    id = Column(String, primary_key=True)
    user_question = Column(Text)
    ai_response = Column(Text)
    context_applications = Column(JSON)
    sources = Column(JSON)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_feedback = Column(String)  # 'helpful', 'not_helpful', null

# Database engine and session
engine = None
SessionLocal = None

def init_db():
    """Initialize database and create all tables"""
    global engine, SessionLocal

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Create engine
    engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine

def get_session():
    """Get a new database session"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()

def close_session(session):
    """Close database session"""
    session.close()

# Initialize on import
init_db()
