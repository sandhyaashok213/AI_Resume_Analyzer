from app.services.analyzer import extract_skills, calculate_match

def test_extract_skills_case_insensitive_and_unique():
    assert extract_skills('Python, PYTHON and React with SQL') == ['python','react','sql']

def test_match_score_uses_job_skill_overlap():
    score, matched, missing, additional = calculate_match('Python React SQL', 'Need Python, React, Docker', [])
    assert score == 66.7
    assert matched == ['python','react']
    assert missing == ['docker']
    assert additional == ['sql']

def test_no_recognized_job_skills_is_zero_not_fake_score():
    score, matched, missing, additional = calculate_match('A resume with work history', 'Seeking a motivated team player', [])
    assert score == 0 and matched == [] and missing == []
