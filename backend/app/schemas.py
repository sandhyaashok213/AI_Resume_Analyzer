from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class AnalysisResponse(BaseModel):
    id: int
    resume_name: str
    job_title: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    strengths: List[str]
    improvements: List[str]
    improved_summary: str
    recommendations: List[str]
    recommended_roles: List[str]
    created_at: datetime

class AnalysisListItem(BaseModel):
    id: int
    resume_name: str
    job_title: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    status: str
    created_at: datetime

class DashboardStats(BaseModel):
    resumes_analyzed: int
    average_match_score: float
    skills_identified: int
    jobs_matched: int

class HealthResponse(BaseModel):
    status: str
    ollama_configured: bool
    model: str
