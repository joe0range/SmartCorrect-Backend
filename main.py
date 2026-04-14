import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from groq import Groq, APIStatusError, APIConnectionError
app = FastAPI(title = "SmartCorrect API", version = "1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["https://smartcorrect-frontend.vercel.app", "http://localhost:3000"],
    allow_methods = ["POST", "GET"],
    allow_headers = ["*"],
)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key = api_key)
MODE_INSTRUCTIONS: dict[str, str] = {
    "standard": "Fix all grammar, spelling, punctuation, and contextual errors. Preserve the author's original voice.",
    "formal":   "Fix all errors AND elevate the tone to be professional and formal. Remove contractions and use precise vocabulary.",
    "casual":   "Fix clear errors but preserve the casual, conversational tone. Do not over-formalize.",
    "academic": "Fix all errors AND ensure academic rigor: use passive voice where appropriate, precise terminology, and no contractions.",
}
SYSTEM_PROMPT_TEMPLATE = """\
You are SmartCorrect, an expert AI grammar and style corrector.
{mode_instruction}
Respond ONLY with a valid JSON object (no markdown fences, no extra text) in exactly this structure:
{{
  "corrected": "The fully corrected text here",
  "score": <integer 0-100 representing original text quality>,
  "corrections": [
    {{
      "type": "grammar|style|clarity",
      "original": "exact original phrase",
      "fixed": "corrected phrase",
      "reason": "brief explanation"
    }}
  ]
}}
Rules:
- "corrected" must be the FULL corrected text
- "score" rates the ORIGINAL text quality (100 = perfect, 0 = very poor)
- List EVERY distinct correction made
- "type" must be exactly one of: "grammar", "style", "clarity"
- Keep the JSON strictly valid — no trailing commas, no comments
"""
class CorrectRequest(BaseModel):
    text: str = Field(..., min_length = 1, max_length = 5000, description = "Text to correct")
    mode: str = Field("standard", description = "Correction mode: standard | formal | casual | academic")
class Correction(BaseModel):
    type: str
    original: str
    fixed: str
    reason: str
class CorrectResponse(BaseModel):
    corrected: str
    score: int
    corrections: list[Correction]
@app.get("/health")
def health():
    return {"status": "ok"}
@app.post("/api/correct", response_model = CorrectResponse)
def correct_text(req: CorrectRequest):
    mode = req.mode if req.mode in MODE_INSTRUCTIONS else "standard"
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        mode_instruction = MODE_INSTRUCTIONS[mode]
    )
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": req.text},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
    except APIStatusError as e:
        raise HTTPException(status_code=502, detail=f"Groq API error: {e.message}")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="Could not reach Groq API")
 
    raw = response.choices[0].message.content or ""
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code = 500, detail = f"Failed to parse model response as JSON: {exc}")
    if "corrected" not in data:
        raise HTTPException(status_code = 500, detail = "Model response missing 'corrected' field")
    corrections = [
        Correction(
            type = c.get("type", "grammar"),
            original = c.get("original", ""),
            fixed = c.get("fixed", ""),
            reason = c.get("reason", ""),
        )
        for c in data.get("corrections", [])
    ]
    return CorrectResponse(
        corrected = data["corrected"],
        score = int(data.get("score", 80)),
        corrections = corrections,
    )
