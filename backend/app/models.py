from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class ResumeAnalysis(Base):
    __tablename__ = 'resume_analyses'
    id = Column(Integer, primary_key=True, index=True)
    resume_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=False)
    resume_text = Column(Text, nullable=False)
    skills = Column(Text, default='[]')
    result_json = Column(Text, nullable=False)
    match_score = Column(Float, default=0)
    status = Column(String(32), default='completed')
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(80), nullable=False)
    message = Column(String(500), nullable=False)
    analysis_id = Column(Integer, ForeignKey('resume_analyses.id'), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
