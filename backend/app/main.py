
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .database import Base, engine
from .routers import resumes, dashboard, jobs
from .ai.ollama import GROQ_MODEL

load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="AI Resume Analyzer API",
    version="1.0.0",
    description="AI-powered resume analysis and job matching using Groq.",
)

# Configure CORS
default_origins = "http://localhost:5173,https://ai-resume-analyzer-iota-lac.vercel.app"

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(resumes.router)
app.include_router(dashboard.router)
app.include_router(jobs.router)


# Health check
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_provider": "Groq",
        "model": GROQ_MODEL,
        "configured": bool(os.getenv("GROQ_API_KEY")),
    }


# Root endpoint
@app.get("/")
def root():
    return {
        "name": "AI Resume Analyzer API",
        "docs": "/docs",
        "health": "/api/health",
    }
