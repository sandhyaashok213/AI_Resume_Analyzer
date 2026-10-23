import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
import fitz
from ..database import get_db
from ..models import ResumeAnalysis, Activity
from ..ai.ollama import analyze_with_ollama
from ..services.analyzer import calculate_match

router = APIRouter(prefix='/api/resumes', tags=['resumes'])
MAX_BYTES = 8 * 1024 * 1024

@router.post('/analyze')
async def analyze_resume(file: UploadFile = File(...), job_title: str = Form(...), job_description: str = Form(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, 'Please upload a PDF resume.')
    if not job_title.strip(): raise HTTPException(422, 'Job title is required.')
    if len(job_description.strip()) < 30: raise HTTPException(422, 'Please enter a job description with at least 30 characters.')
    if len(job_description) > 10000: raise HTTPException(422, 'Job description must be 10,000 characters or fewer.')
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES: raise HTTPException(413, 'PDF is too large. Maximum file size is 8 MB.')
    if not raw.startswith(b'%PDF'): raise HTTPException(400, 'The uploaded file is not a valid PDF.')
    try:
        with fitz.open(stream=raw, filetype='pdf') as doc:
            resume_text = '\n'.join(page.get_text() for page in doc).strip()
    except Exception as exc: raise HTTPException(400, 'Could not read this PDF. Try exporting it again as a text-based PDF.') from exc
    if len(resume_text) < 40: raise HTTPException(422, 'No readable resume text found. Scanned PDFs need OCR before analysis.')
    try: ai = await analyze_with_ollama(resume_text, job_description)
    except RuntimeError as exc: raise HTTPException(503, str(exc)) from exc
    score, matched, missing, additional = calculate_match(resume_text, job_description, ai['resume_skills'])
    result = {**ai, 'matched_skills': matched, 'missing_skills': missing, 'additional_skills': additional,
              'match_score': score, 'score_method': 'Recognized job-description skill overlap: matched recognized skills / all recognized job-description skills. This is an estimate, not a hiring prediction.'}
    row = ResumeAnalysis(resume_name=file.filename[:255], job_title=job_title.strip()[:255], job_description=job_description.strip(), resume_text=resume_text[:25000], skills=json.dumps(sorted(set(ai['resume_skills']) | set(matched) | set(additional))), result_json=json.dumps(result), match_score=score, status='completed')
    db.add(row); db.commit(); db.refresh(row)
    for event, message in [('resume_uploaded', f'Uploaded {row.resume_name}'), ('analysis_completed', f'Analysis completed for {row.job_title}'), ('job_match_calculated', f'Calculated a {score:g}% skill-overlap score')]:
        db.add(Activity(event_type=event, message=message, analysis_id=row.id))
    db.commit()
    return {'id': row.id, 'resume_name': row.resume_name, 'job_title': row.job_title, **result, 'created_at': row.created_at}

@router.get('')
def list_resumes(q: str = '', sort: str = 'newest', skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(ResumeAnalysis)
    if q.strip(): query = query.filter((ResumeAnalysis.resume_name.ilike(f'%{q.strip()}%')) | (ResumeAnalysis.job_title.ilike(f'%{q.strip()}%')))
    query = query.order_by(ResumeAnalysis.match_score.asc() if sort == 'score_asc' else ResumeAnalysis.match_score.desc() if sort == 'score_desc' else ResumeAnalysis.created_at.asc() if sort == 'oldest' else ResumeAnalysis.created_at.desc())
    rows = query.offset(max(skip,0)).limit(min(max(limit,1),100)).all()
    return [{'id':r.id,'resume_name':r.resume_name,'job_title':r.job_title,'match_score':r.match_score,'matched_skills':json.loads(r.result_json).get('matched_skills',[]),'missing_skills':json.loads(r.result_json).get('missing_skills',[]),'status':r.status,'created_at':r.created_at} for r in rows]

@router.get('/{analysis_id}')
def get_resume(analysis_id: int, db: Session = Depends(get_db)):
    r = db.query(ResumeAnalysis).filter_by(id=analysis_id).first()
    if not r: raise HTTPException(404, 'Analysis not found.')
    return {'id':r.id,'resume_name':r.resume_name,'job_title':r.job_title,'match_score':r.match_score,'created_at':r.created_at,**json.loads(r.result_json)}

@router.delete('/{analysis_id}')
def delete_resume(analysis_id: int, db: Session = Depends(get_db)):
    r = db.query(ResumeAnalysis).filter_by(id=analysis_id).first()
    if not r: raise HTTPException(404, 'Analysis not found.')
    db.query(Activity).filter_by(analysis_id=analysis_id).delete(); db.delete(r); db.commit()
    return {'deleted': True, 'id': analysis_id}
