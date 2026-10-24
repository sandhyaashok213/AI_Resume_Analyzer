
import json
import os
import re

import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

SYSTEM_PROMPT = """
You are a careful resume reviewer. Use ONLY evidence from the supplied
resume and job description. Do not invent skills, education, employers,
experience, or achievements.

Return one valid JSON object with these keys:
resume_skills (array of strings),
strengths (array of strings),
improvements (array of strings),
improved_summary (string),
recommendations (array of strings),
recommended_roles (array of strings).

Keep suggestions actionable. Never claim unsupported experience.
Return JSON only, without markdown fences.
"""


async def analyze_with_ollama(
    resume_text: str,
    job_description: str,
) -> dict:
    """Analyze a resume using the hosted Groq API."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your backend environment variables."
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"RESUME TEXT:\n{resume_text[:18000]}\n\n"
                    f"JOB DESCRIPTION:\n{job_description[:10000]}"
                ),
            },
        ],
        "temperature": 0.1,
        "max_completion_tokens": 4000,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()

        content = result["choices"][0]["message"]["content"]
        content = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            content.strip(),
            flags=re.IGNORECASE,
        )
        data = json.loads(content)

        required = [
            "resume_skills",
            "strengths",
            "improvements",
            "improved_summary",
            "recommendations",
            "recommended_roles",
        ]

        if not isinstance(data, dict):
            raise ValueError("The model did not return a JSON object.")

        if any(key not in data for key in required):
            raise ValueError("The model response is missing required fields.")

        for key in required:
            if key == "improved_summary":
                data[key] = (
                    str(data[key])[:3000]
                    if data[key] is not None
                    else ""
                )
            else:
                value = data[key]
                data[key] = (
                    [str(item)[:400] for item in value
                     if str(item).strip()][:15]
                    if isinstance(value, list)
                    else []
                )

        return data

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 401:
            message = "Groq rejected the API key. Check GROQ_API_KEY."
        elif status == 429:
            message = "Groq rate limit reached. Wait and try again."
        else:
            message = f"Groq API returned HTTP {status}."
        raise RuntimeError(message) from exc

    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Could not connect to the Groq API: {exc}"
        ) from exc

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        raise RuntimeError(
            f"Could not parse the AI response: {exc}"
        ) from exc
