# AI-Powered Multimodal Construction Intelligence Platform

Full-stack decision-support system for construction planning, execution and monitoring. Analyzes text, site images and structured data with a multimodal LLM.

**Stack:** React.js (Vite) · FastAPI (Python) · Multimodal LLM (Claude) · HTML5 · CSS

## Features
Site safety monitoring · Crack detection · Real estate valuation · Project planning · Daily site assistant · Weather-aware advisory (Open-Meteo) · Construction knowledge assistant

Every endpoint (`POST /api/{feature}`) returns a strict JSON contract: `{"feature": "...", "result": {...}}`.

## Run locally
**Backend**
```
cd backend
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Mac/Linux: cp .env.example .env  -> add ANTHROPIC_API_KEY
uvicorn main:app --reload
```
**Frontend** (new terminal)
```
cd frontend
copy .env.example .env       # Mac/Linux: cp
npm install
npm run dev
```
Open http://localhost:5173 (API docs: http://localhost:8000/docs).
