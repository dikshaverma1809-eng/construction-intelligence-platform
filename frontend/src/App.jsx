import { useState } from "react";
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const FEATURES = [
  { id: "safety", title: "Safety Monitoring", image: true, fields: [{ k: "notes", label: "Site notes (optional)" }] },
  { id: "crack", title: "Crack Detection", image: true, fields: [{ k: "location", label: "Location of crack (wall, beam...)" }] },
  { id: "valuation", title: "Real Estate Valuation", fields: [
    { k: "city", label: "City" }, { k: "area_sqft", label: "Area (sq ft)", type: "number" },
    { k: "bedrooms", label: "Bedrooms", type: "number" }, { k: "age_years", label: "Age (years)", type: "number" }] },
  { id: "planning", title: "Project Planning", fields: [
    { k: "project", label: "Project (e.g. 3-floor residential building)" }, { k: "budget_inr", label: "Budget (INR)", type: "number" },
    { k: "deadline_weeks", label: "Deadline (weeks)", type: "number" }] },
  { id: "assistant", title: "Daily Site Assistant", fields: [
    { k: "stage", label: "Current stage (e.g. slab casting)" }, { k: "workers", label: "Workers on site", type: "number" }] },
  { id: "weather", title: "Weather Advisory", fields: [{ k: "city", label: "Site city" }, { k: "activity", label: "Planned activity" }] },
  { id: "knowledge", title: "Knowledge Assistant", fields: [{ k: "question", label: "Ask a construction question" }] },
];

function Result({ data }) {
  if (Array.isArray(data)) return <ul>{data.map((d, i) => <li key={i}><Result data={d} /></li>)}</ul>;
  if (data && typeof data === "object")
    return <dl>{Object.entries(data).map(([k, v]) => <div key={k}><dt>{k.replace(/_/g, " ")}</dt><dd><Result data={v} /></dd></div>)}</dl>;
  return <span>{String(data)}</span>;
}

export default function App() {
  const [f, setF] = useState(FEATURES[0]);
  const [vals, setVals] = useState({}); const [file, setFile] = useState(null);
  const [out, setOut] = useState(null); const [err, setErr] = useState(""); const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault(); setBusy(true); setErr(""); setOut(null);
    const fd = new FormData(); fd.append("data", JSON.stringify(vals)); if (file) fd.append("image", file);
    try {
      const r = await fetch(`${API}/api/${f.id}`, { method: "POST", body: fd });
      const j = await r.json(); if (!r.ok) throw new Error(j.detail || "Request failed"); setOut(j.result);
    } catch (x) { setErr(x.message); } finally { setBusy(false); }
  }
  const pick = (x) => { setF(x); setVals({}); setFile(null); setOut(null); setErr(""); };

  return (<div className="app">
    <header><h1>🏗️ Construction Intelligence Platform</h1><p>Multimodal AI for planning, execution & monitoring</p></header>
    <nav>{FEATURES.map(x => <button key={x.id} className={x.id === f.id ? "on" : ""} onClick={() => pick(x)}>{x.title}</button>)}</nav>
    <form onSubmit={submit}>
      <h2>{f.title}</h2>
      {f.image && <label>Upload site image<input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} /></label>}
      {f.fields.map(x => <label key={x.k}>{x.label}
        <input type={x.type || "text"} value={vals[x.k] || ""} onChange={e => setVals({ ...vals, [x.k]: e.target.value })} /></label>)}
      <button disabled={busy}>{busy ? "Analyzing…" : "Analyze"}</button>
    </form>
    {err && <div className="err">{err}</div>}
    {out && <section className="out"><h3>Result</h3><Result data={out} /></section>}
  </div>);
}
