import re

# Skill vocabulary is used only for transparent matching; the LLM adds context, not score authority.
SKILL_TERMS = sorted(set('python java javascript typescript react next.js node.js express fastapi flask django sql sqlite postgresql mysql mongodb redis docker kubernetes aws azure gcp git github linux html css tailwind rest api graphql machine learning deep learning nlp pandas numpy scikit-learn tensorflow pytorch data analysis power bi tableau excel communication leadership agile scrum testing pytest ci/cd'.split()), key=len, reverse=True)

def extract_skills(text: str) -> list[str]:
    normalized = text.lower()
    found = []
    for skill in SKILL_TERMS:
        pattern = r'(?<![a-z0-9+#.])' + re.escape(skill.lower()) + r'(?![a-z0-9+#.])'
        if re.search(pattern, normalized): found.append(skill)
    return sorted(set(found))

def calculate_match(resume_text: str, job_description: str, resume_skills: list[str]) -> tuple[float,list[str],list[str],list[str]]:
    # Scores use only deterministic matches from source text; AI-extracted terms never inflate the score.
    resume_found = set(extract_skills(resume_text))
    job_found = set(extract_skills(job_description))
    matched = sorted(resume_found & job_found)
    missing = sorted(job_found - resume_found)
    additional = sorted(resume_found - job_found)
    # Skill overlap is the primary score. When no recognized skills exist, avoid fabricating a score.
    score = round(100 * len(matched) / len(job_found), 1) if job_found else 0.0
    return score, matched, missing, additional
