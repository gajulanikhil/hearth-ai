"""
app.py — Hearth web application (FastAPI backend + SPA frontend)

Run with:
    python app.py
or:
    uvicorn app:app --reload --port 8000
"""

import asyncio
import json
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import memory_bank

app = FastAPI(title="Hearth", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static assets (CSS, JS if separated later)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

# In-memory job store and thread pool for blocking agent calls
jobs: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=4)


# ── HTML ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")


# ── Status ────────────────────────────────────────────────────────────────────

@app.get("/api/status")
async def status():
    """Report whether Claude API is available."""
    try:
        import anthropic
        key = os.getenv("ANTHROPIC_API_KEY") or None
        client = anthropic.Anthropic(api_key=key)
        # Attempt a tiny call to check auth
        client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            messages=[{"role": "user", "content": "hi"}],
        )
        return {"claude_available": True, "mode": "live"}
    except Exception:
        return {"claude_available": False, "mode": "demo"}


# ── Patients ──────────────────────────────────────────────────────────────────

@app.get("/api/patients")
async def list_patients():
    patients_dir = ROOT / "data" / "patients"
    if not patients_dir.exists():
        return []

    result = []
    for d in sorted(patients_dir.iterdir()):
        if not d.is_dir() or not (d / "profile.json").exists():
            continue
        profile = memory_bank.load_profile(d.name)
        memories = memory_bank.load_memories(d.name)
        photos = memory_bank.list_photos(d.name)

        output_dir = ROOT / "data" / "outputs" / d.name
        recent_run = None
        if output_dir.exists():
            runs = sorted(output_dir.iterdir(), reverse=True)
            if runs:
                recent_run = runs[0].name

        result.append({
            "id": d.name,
            "profile": profile,
            "memory_count": len(memories),
            "photo_count": len(photos),
            "recent_run": recent_run,
        })
    return result


@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    if not memory_bank.patient_exists(patient_id):
        raise HTTPException(404, f"Patient '{patient_id}' not found.")

    profile = memory_bank.load_profile(patient_id)
    memories = memory_bank.load_memories(patient_id)
    photos = memory_bank.list_photos(patient_id)

    output_dir = ROOT / "data" / "outputs" / patient_id
    artifact_runs = []
    if output_dir.exists():
        for run_dir in sorted(output_dir.iterdir(), reverse=True)[:5]:
            if run_dir.is_dir():
                files = [f.name for f in sorted(run_dir.iterdir())]
                artifact_runs.append({"timestamp": run_dir.name, "files": files})

    return {
        "id": patient_id,
        "profile": profile,
        "memories": memories,
        "photos": photos,
        "artifact_runs": artifact_runs,
    }


# ── Profile creation / update ─────────────────────────────────────────────────

class ProfileRequest(BaseModel):
    name: str
    age: int = 0
    stage: str = "moderate"
    primary_family_contact: str = ""
    emotional_anchors: list[str] = []
    calming_topics: list[str] = []
    avoid_topics: list[str] = []
    current_mood_baseline: str = ""
    best_time_of_day: str = ""


def _name_to_id(name: str) -> str:
    import re
    return re.sub(r"[^a-z0-9_]", "", name.lower().replace(" ", "_"))


@app.post("/api/patients")
async def create_patient(req: ProfileRequest):
    patient_id = _name_to_id(req.name)
    profile = req.model_dump()
    memory_bank.save_profile(patient_id, profile)
    return {"patient_id": patient_id}


@app.put("/api/patients/{patient_id}/profile")
async def update_profile(patient_id: str, req: ProfileRequest):
    if memory_bank.patient_exists(patient_id):
        profile = memory_bank.load_profile(patient_id)
        profile.update(req.model_dump(exclude_none=True))
    else:
        profile = req.model_dump()
    memory_bank.save_profile(patient_id, profile)
    return {"success": True}


# ── Memory submission ─────────────────────────────────────────────────────────

class MemoryRequest(BaseModel):
    submitted_by: str
    relationship: str
    memory_text: str
    emotional_tone: str = "warm"
    associated_photos: list[str] = []
    voice_sample_file: Optional[str] = None


@app.post("/api/patients/{patient_id}/memories")
async def add_memory(patient_id: str, req: MemoryRequest):
    if not memory_bank.patient_exists(patient_id):
        raise HTTPException(404, "Patient not found. Create profile first.")

    profile = memory_bank.load_profile(patient_id)
    if not profile.get("primary_family_contact"):
        profile["primary_family_contact"] = f"{req.submitted_by} ({req.relationship})"
        memory_bank.save_profile(patient_id, profile)

    memory = req.model_dump(exclude_none=True)
    memory_bank.add_memory(patient_id, memory)
    return {"success": True}


# ── File uploads ──────────────────────────────────────────────────────────────

@app.post("/api/patients/{patient_id}/upload_photo")
async def upload_photo(patient_id: str, file: UploadFile = File(...)):
    photos_dir = memory_bank.get_photos_dir(patient_id)
    photos_dir.mkdir(parents=True, exist_ok=True)
    dest = photos_dir / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"success": True, "filename": file.filename}


@app.post("/api/patients/{patient_id}/upload_voice")
async def upload_voice(patient_id: str, file: UploadFile = File(...)):
    voice_dir = memory_bank.get_voice_samples_dir(patient_id)
    voice_dir.mkdir(parents=True, exist_ok=True)
    dest = voice_dir / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"success": True, "filename": file.filename}


# ── Demo setup ────────────────────────────────────────────────────────────────

def _setup_demo_sync():
    import importlib.util, io
    spec = importlib.util.spec_from_file_location("setup_demo", ROOT / "sample_data" / "setup_demo.py")
    mod = importlib.util.module_from_spec(spec)
    # Redirect stdout to suppress print output
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
        mod.create_demo()


@app.post("/api/demo/setup")
async def setup_demo():
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(executor, _setup_demo_sync)
        return {"success": True, "patient_id": "margaret_chen"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Lucid Now ────────────────────────────────────────────────────────────────

def _run_lucid_now(patient_id: str, job_id: str):
    """Blocking function — runs in thread pool."""
    job = jobs[job_id]
    job["status"] = "running"

    try:
        profile = memory_bank.load_profile(patient_id)
        memories = memory_bank.load_memories(patient_id)
        photo_info = memory_bank.get_photo_context(patient_id, memories)
        photos_dir = memory_bank.get_photos_dir(patient_id)
        voice_samples_dir = memory_bank.get_voice_samples_dir(patient_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = ROOT / "data" / "outputs" / patient_id / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        job["timestamp"] = timestamp

        results = {}

        # Detect whether real agent is available
        use_demo = True
        try:
            from agent import HearthAgent
            agent = HearthAgent()
            # Try a tiny call
            import anthropic as _anth
            _anth.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY") or None).messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=5,
                messages=[{"role": "user", "content": "hi"}],
            )
            use_demo = False
        except Exception:
            use_demo = True

        # ── Letter ───────────────────────────────────────────────────────────
        job["steps"]["letter"] = "running"
        try:
            if use_demo:
                from demo_run import LETTER_TEXT as letter_text
            else:
                letter_text = agent.generate_letter(profile, memories)

            from letter_generator import generate_letter_pdf
            p = output_dir / f"letter_{patient_id}_{timestamp}.pdf"
            generate_letter_pdf(letter_text, profile, p)
            results["letter"] = p.name
            job["steps"]["letter"] = "done"
        except Exception as e:
            job["steps"]["letter"] = f"error"
            job["errors"]["letter"] = str(e)

        # ── Voice ────────────────────────────────────────────────────────────
        job["steps"]["voice"] = "running"
        try:
            if use_demo:
                from demo_run import VOICE_SCRIPT as voice_script
            else:
                voice_script = agent.generate_voice_script(profile, memories)

            from voice_generator import generate_voice_message
            p = output_dir / f"voice_{patient_id}_{timestamp}.mp3"
            final_path, is_audio = generate_voice_message(
                voice_script, profile, voice_samples_dir, memories, p
            )
            results["voice"] = final_path.name
            results["voice_is_audio"] = is_audio
            job["steps"]["voice"] = "done"
        except Exception as e:
            job["steps"]["voice"] = "error"
            job["errors"]["voice"] = str(e)

        # ── Photo story ───────────────────────────────────────────────────────
        job["steps"]["photo_story"] = "running"
        try:
            if photo_info:
                if use_demo:
                    from demo_run import PHOTO_CAPTIONS as captions
                else:
                    captions = agent.generate_photo_captions(profile, memories, photo_info)

                from photo_story import generate_photo_story_pdf
                p = output_dir / f"photo_story_{patient_id}_{timestamp}.pdf"
                generate_photo_story_pdf(captions, profile, photos_dir, p)
                results["photo_story"] = p.name
                job["steps"]["photo_story"] = "done"
            else:
                job["steps"]["photo_story"] = "skipped"
        except Exception as e:
            job["steps"]["photo_story"] = "error"
            job["errors"]["photo_story"] = str(e)

        # ── Dialogue guide ────────────────────────────────────────────────────
        job["steps"]["dialogue_guide"] = "running"
        try:
            if use_demo:
                from demo_run import DIALOGUE_GUIDE as guide
            else:
                guide = agent.generate_dialogue_guide(profile, memories)

            from dialogue_guide import generate_dialogue_guide_pdf
            p = output_dir / f"dialogue_guide_{patient_id}_{timestamp}.pdf"
            generate_dialogue_guide_pdf(guide, profile, p)
            results["dialogue_guide"] = p.name
            job["steps"]["dialogue_guide"] = "done"
        except Exception as e:
            job["steps"]["dialogue_guide"] = "error"
            job["errors"]["dialogue_guide"] = str(e)

        job["results"] = results
        job["status"] = "done"
        job["mode"] = "demo" if use_demo else "live"

    except Exception as e:
        job["status"] = "error"
        job["errors"]["general"] = str(e)


@app.post("/api/patients/{patient_id}/lucid_now")
async def start_lucid_now(patient_id: str):
    if not memory_bank.patient_exists(patient_id):
        raise HTTPException(404, "Patient not found")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "patient_id": patient_id,
        "status": "pending",
        "steps": {
            "letter": "pending",
            "voice": "pending",
            "photo_story": "pending",
            "dialogue_guide": "pending",
        },
        "errors": {},
        "results": {},
        "timestamp": None,
        "mode": None,
    }

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, _run_lucid_now, patient_id, job_id)
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]


@app.get("/api/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """Server-Sent Events stream for real-time job progress."""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    async def event_generator():
        prev = None
        while True:
            job = jobs.get(job_id, {})
            current = json.dumps(job)
            if current != prev:
                yield f"data: {current}\n\n"
                prev = current
            if job.get("status") in ("done", "error"):
                break
            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── File serving ──────────────────────────────────────────────────────────────

@app.get("/api/files/{patient_id}/{timestamp}/{filename}")
async def serve_artifact(patient_id: str, timestamp: str, filename: str):
    path = ROOT / "data" / "outputs" / patient_id / timestamp / filename
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(str(path))


@app.get("/api/photos/{patient_id}/{filename}")
async def serve_photo(patient_id: str, filename: str):
    path = memory_bank.get_photos_dir(patient_id) / filename
    if not path.exists():
        raise HTTPException(404, "Photo not found")
    return FileResponse(str(path))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Hearth is starting...")
    print("  Open http://localhost:8000 in your browser.\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
