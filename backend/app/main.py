import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import resumes, dashboard, jobs
from .ai.ollama import OLLAMA_MODEL, OLLAMA_URL
import httpx

Base.metadata.create_all(bind=engine)
app = FastAPI(title='AI Resume Analyzer API', version='1.0.0', description='Resume-to-job matching powered by local Ollama.')
origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in origins], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(resumes.router); app.include_router(dashboard.router); app.include_router(jobs.router)
@app.get('/api/health')
async def health():
    reachable = False
    try:
        async with httpx.AsyncClient(timeout=2) as client: reachable = (await client.get(f'{OLLAMA_URL.rstrip("/")}/api/tags')).is_success
    except Exception: pass
    return {'status':'ok','ollama_configured':reachable,'model':OLLAMA_MODEL,'message':None if reachable else f'Ollama is not reachable at {OLLAMA_URL}. Start Ollama and run: ollama pull {OLLAMA_MODEL}'}
@app.get('/')
def root(): return {'name':'AI Resume Analyzer API','docs':'/docs','health':'/api/health'}
