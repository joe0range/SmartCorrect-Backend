# SmartCorrect — AI Autocorrect Tool

A full-stack AI autocorrect application powered by Groq.  
**Backend:** Python + FastAPI  
**Frontend:** Vanilla HTML / CSS / JavaScript

---

## Project Structure

```
SmartCorrect/
├── Backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── Frontend/
│   └── index.html        # Single-file frontend
└── README.md
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10 + |
| pip | latest |
| Groq API key | — |

---

## Setup & Run

### 1. Clone / download the project

```bash
git clone <your-repo-url>
cd smartscript
```

### 2. Set your Groq API key

```bash
# Linux / macOS
export GROQ_API_KEY="sk-ant-..."

# Windows PowerShell
$env:GROQ_API_KEY = "sk-ant-..."

# Windows CMD
set GROQ_API_KEY=sk-ant-...
```

### 3. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Start the backend

```bash
# From the backend/ directory
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### 5. Open the frontend

Open `frontend/index.html` directly in your browser:

```bash
# macOS
open ../frontend/index.html

# Linux
xdg-open ../frontend/index.html

# Windows
start ..\frontend\index.html
```

Or serve it with any static server:

```bash
# Using Python's built-in server (from the frontend/ directory)
cd ../frontend
python -m http.server 3000
# Then visit http://localhost:3000
```

---

## API Reference

### `POST /api/correct`

Correct text and return structured results.

**Request body**
```json
{
  "text": "Their going to the store tomorrow, he said.",
  "mode": "standard"
}
```

| Field | Type   | Description |
|-------|--------|-------------|
| `text` | string | Text to correct (1 – 5000 chars) |
| `mode` | string | `standard` \| `formal` \| `casual` \| `academic` |

**Response body**
```json
{
  "corrected": "They're going to the store tomorrow, he said.",
  "score": 72,
  "corrections": [
    {
      "type": "grammar",
      "original": "Their going",
      "fixed": "They're going",
      "reason": "\"Their\" is possessive; \"They're\" (they are) is correct here."
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `corrected` | string | Fully corrected text |
| `score` | integer (0–100) | Quality score of the **original** text |
| `corrections` | array | List of individual corrections |
| `corrections[].type` | string | `grammar` / `style` / `clarity` |
| `corrections[].original` | string | Original phrase |
| `corrections[].fixed` | string | Corrected phrase |
| `corrections[].reason` | string | Plain-English explanation |

### `GET /health`

Returns `{"status": "ok"}` — useful for container health checks.

---

## Correction Modes

| Mode | Behaviour |
|------|-----------|
| **Standard** | Fix all errors, preserve the author's voice |
| **Formal** | Fix errors + elevate to professional tone, remove contractions |
| **Casual** | Fix clear errors only, keep conversational feel |
| **Academic** | Fix errors + enforce academic style (precise vocabulary, no contractions) |

---

## Production Deployment Tips

1. **Serve the frontend from FastAPI** — uncomment the `StaticFiles` mount at the bottom of `main.py`, build/copy `frontend/` to the right path, and drop the CORS wildcard.
2. **Store secrets securely** — use a `.env` file with `python-dotenv` or your cloud provider's secret manager instead of exporting env vars manually.
3. **Rate limit the API** — add `slowapi` or an API gateway in front to prevent abuse.
4. **HTTPS** — always run behind a reverse proxy (nginx, Caddy) with TLS in production.
