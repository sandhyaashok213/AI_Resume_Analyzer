import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ResumeAnalysis, Activity

router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])

@router.get('/stats')
def stats(db: Session = Depends(get_db)):
    rows = db.query(ResumeAnalysis).all(); skills = set(); roles = set()
    for r in rows:
        skills.update(json.loads(r.skills or '[]')); roles.add(r.job_title.lower())
    return {'resumes_analyzed':len(rows),'average_match_score':round(sum(r.match_score for r in rows)/len(rows),1) if rows else 0,'skills_identified':len(skills),'jobs_matched':len(roles)}

@router.get('/activity')
def activity(limit: int = 8, db: Session = Depends(get_db)):
    rows = db.query(Activity).order_by(Activity.created_at.desc()).limit(min(max(limit,1),50)).all()
    return [{'id':r.id,'event_type':r.event_type,'message':r.message,'analysis_id':r.analysis_id,'created_at':r.created_at} for r in rows]

@router.get('/analytics')
def analytics(period: str = 'week', db: Session = Depends(get_db)):
    days = {'day':1,'week':7,'month':30,'year':365}.get(period,7)
    start = datetime.now(timezone.utc) - timedelta(days=days-1)
    rows = db.query(ResumeAnalysis).filter(ResumeAnalysis.created_at >= start.replace(tzinfo=None)).order_by(ResumeAnalysis.created_at.asc()).all()
    buckets = {}
    for i in range(days):
        d = (start + timedelta(days=i)).date().isoformat(); buckets[d] = {'date':d,'analyses':0,'average_score':0,'_sum':0}
    for r in rows:
        key = r.created_at.date().isoformat()
        if key in buckets: buckets[key]['analyses'] += 1; buckets[key]['_sum'] += r.match_score
    for v in buckets.values(): v['average_score'] = round(v['_sum']/v['analyses'],1) if v['analyses'] else 0; del v['_sum']
    return list(buckets.values())
