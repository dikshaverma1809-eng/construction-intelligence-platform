import os, json, base64, httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import anthropic

load_dotenv()
app = FastAPI(title="AI-Powered Multimodal Construction Intelligence Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
MODEL = os.getenv("MODEL", "claude-sonnet-4-6")

# Strict JSON contracts: the frontend relies on these exact shapes.
CONTRACTS = {
 "safety": ("You are a construction site safety inspector. Analyze the site image/notes for PPE, hazards, housekeeping.",
   '{"risk_level":"low|medium|high","violations":[{"issue":"","severity":"low|medium|high","fix":""}],"summary":""}'),
 "crack": ("You are a structural engineer. Analyze the image for cracks: type, likely cause, severity.",
   '{"crack_type":"","severity":"minor|moderate|severe","probable_causes":[""],"repair_steps":[""],"urgent":false}'),
 "valuation": ("You are a real estate valuation analyst for India. Estimate value from the property details.",
   '{"estimated_value_inr":0,"price_per_sqft_inr":0,"range_low_inr":0,"range_high_inr":0,"factors":[""],"summary":""}'),
 "planning": ("You are a construction project planner. Create a phased plan with timeline and budget split.",
   '{"phases":[{"name":"","duration_weeks":0,"tasks":[""],"budget_percent":0}],"total_weeks":0,"risks":[""]}'),
 "assistant": ("You are a daily site assistant. Produce today's priorities, checklist and safety reminders.",
   '{"priorities":[""],"checklist":[""],"safety_reminders":[""],"summary":""}'),
 "weather": ("You are a weather-aware construction advisor. Use the forecast data to advise on site work.",
   '{"overall":"go|caution|stop","activities_ok":[""],"activities_avoid":[""],"precautions":[""],"summary":""}'),
 "knowledge": ("You are a construction knowledge expert (codes, materials, methods, IS standards).",
   '{"answer":"","key_points":[""],"references":[""]}'),
}

async def forecast(city: str):
    async with httpx.AsyncClient(timeout=15) as h:
        g = (await h.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1})).json()
        if not g.get("results"): raise HTTPException(404, "City not found")
        r = g["results"][0]
        f = (await h.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": r["latitude"], "longitude": r["longitude"], "timezone": "auto", "forecast_days": 3,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"})).json()
        return {"city": r["name"], "daily": f["daily"]}

@app.get("/")
def health(): return {"status": "ok", "features": list(CONTRACTS)}

@app.post("/api/{feature}")
async def run(feature: str, data: str = Form("{}"), image: UploadFile | None = File(None)):
    if feature not in CONTRACTS: raise HTTPException(404, "Unknown feature")
    role, schema = CONTRACTS[feature]
    payload = json.loads(data)
    if feature == "weather":
        payload["forecast"] = await forecast(payload.get("city", "Indore"))
    content = []
    if image:
        raw = await image.read()
        content.append({"type": "image", "source": {"type": "base64",
            "media_type": image.content_type or "image/jpeg", "data": base64.b64encode(raw).decode()}})
    content.append({"type": "text", "text": f"Input: {json.dumps(payload)}"})
    try:
        msg = client.messages.create(model=MODEL, max_tokens=1500,
            system=f"{role} Respond with ONLY valid JSON, no markdown, matching exactly: {schema}",
            messages=[{"role": "user", "content": content}])
        text = msg.content[0].text.strip().strip("`").removeprefix("json").strip()
        return {"feature": feature, "result": json.loads(text)}
    except json.JSONDecodeError:
        raise HTTPException(502, "Model returned invalid JSON")
    except Exception as e:
        raise HTTPException(500, str(e))
