import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ResumeAnalysis
router = APIRouter(prefix='/api/jobs', tags=['jobs'])
@router.get('/recommendations')
def recommendations(db: Session = Depends(get_db)):
    rows = db.query(ResumeAnalysis).order_by(ResumeAnalysis.created_at.desc()).limit(20).all(); items=[]
    for r in rows:
        result=json.loads(r.result_json)
        for role in result.get('recommended_roles',[]):
            items.append({'role':role,'source_resume':r.resume_name,'match_score':r.match_score,'matched_skills':result.get('matched_skills',[]),'missing_skills':result.get('missing_skills',[]),'analysis_id':r.id})
    return items[:50]
