import json, os, re
from dotenv import load_dotenv
import httpx

load_dotenv()

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2')

SYSTEM_PROMPT = '''You are a careful resume reviewer. Use ONLY evidence from the supplied resume and job description. Do not invent skills, education, employers, experience, or achievements. Return one valid JSON object with keys: resume_skills (array of strings), strengths (array of strings), improvements (array of strings), improved_summary (string), recommendations (array of strings), recommended_roles (array of strings). Keep suggestions actionable and clearly avoid claiming unsupported experience. No markdown fences.'''

async def analyze_with_ollama(resume_text: str, job_description: str) -> dict:
    payload = {'model': OLLAMA_MODEL, 'stream': False, 'format': 'json', 'messages': [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': f'RESUME TEXT:\n{resume_text[:18000]}\n\nJOB DESCRIPTION:\n{job_description[:10000]}'}
    ], 'options': {'temperature': 0.1}}
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f'{OLLAMA_URL.rstrip("/")}/api/chat', json=payload)
            response.raise_for_status()
            content = response.json().get('message', {}).get('content', '')
        content = re.sub(r'^```(?:json)?\s*|\s*```$', '', content.strip(), flags=re.I)
        data = json.loads(content)
        required = ['resume_skills','strengths','improvements','improved_summary','recommendations','recommended_roles']
        if not isinstance(data, dict) or any(k not in data for k in required):
            raise ValueError('The model response is missing required fields.')
        for key in required:
            if key == 'improved_summary':
                data[key] = str(data[key])[:3000]
            else:
                data[key] = [str(x)[:400] for x in data[key] if str(x).strip()][:15] if isinstance(data[key], list) else []
        return data
    except (httpx.HTTPError, json.JSONDecodeError, ValueError, KeyError) as exc:
        raise RuntimeError(f'Ollama analysis failed ({exc}). Ensure Ollama is running and model "{OLLAMA_MODEL}" is installed. Try: ollama pull {OLLAMA_MODEL}') from exc
