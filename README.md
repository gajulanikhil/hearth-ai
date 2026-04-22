# Hearth

> An AI memory companion for Alzheimer's patients in care homes. When a lucid moment happens, Hearth brings the family into the room — a personal letter, a voice message, a photo story, and a caregiver script, all generated in under a minute from memories the family submitted.

---

## The problem

Alzheimer's patients experience unpredictable **lucid moments** — short windows, sometimes 20 minutes, sometimes 2 hours, where they feel like themselves again. Nobody knows when they'll happen. Families are almost never there when they do. The caregiver witnesses it alone and has nothing personal to give the patient. The moment passes. It may not come back for weeks.

You can't schedule a lucid moment. You can only be ready for one.

## What Hearth does

Family members submit memories **once**, from anywhere — voice recordings, photos, stories, relationships. Hearth reads everything and builds a memory map of the person's life before the disease.

When a lucid moment happens, the caregiver taps one button. In under 60 seconds, Hearth generates four personal artifacts from the family's real memories:

| Artifact | What it is |
|---|---|
| **Letter** | A written letter in the family member's voice, referencing real shared memories. As if they wrote it this morning. |
| **Voice message** | A short audio message synthesized in the family member's actual cloned voice (via ElevenLabs). |
| **Photo story** | Family photos with warm captions the caregiver reads aloud while showing the patient. |
| **Dialogue guide** | A caregiver script — how to open, what to ask, what to show, how to respond if the patient gets anxious, how to close gently. |

The family's love is already there, waiting. The caregiver just delivers it.

---

## Architecture

```
Browser (SPA)
    │
    │  HTTP / Server-Sent Events
    ▼
FastAPI (app.py — port 8000)
    ├── GET  /                        → serves index.html SPA
    ├── GET  /api/patients            → list all patients
    ├── POST /api/patients            → create patient profile
    ├── GET  /api/patients/{id}       → patient detail + artifact history
    ├── PUT  /api/patients/{id}/profile
    ├── DELETE /api/patients/{id}
    ├── POST /api/patients/{id}/memories
    ├── POST /api/patients/{id}/upload_photo
    ├── POST /api/patients/{id}/upload_voice
    ├── POST /api/patients/{id}/lucid_now → enqueues job, returns job_id
    ├── GET  /api/jobs/{job_id}        → job status (polling)
    ├── GET  /api/jobs/{job_id}/stream → SSE real-time progress
    ├── POST /api/chat/stream          → SSE caretaker AI chat
    ├── POST /api/demo/setup           → creates demo patient
    └── GET  /api/files/{patient}/{ts}/{file} → serve generated artifacts
    │
    ├── ThreadPoolExecutor (4 workers)
    │       └── _run_lucid_now()
    │               ├── HearthAgent.generate_letter()      → letter_generator.py → PDF
    │               ├── HearthAgent.generate_voice_script() → voice_generator.py → MP3/TXT
    │               ├── HearthAgent.generate_photo_captions() → photo_story.py → PDF
    │               └── HearthAgent.generate_dialogue_guide() → dialogue_guide.py → PDF
    │
    └── memory_bank.py  (JSON flat-file store)
            data/patients/{id}/profile.json
            data/patients/{id}/memories.json
            data/patients/{id}/photos/
            data/patients/{id}/voice_samples/
            data/outputs/{id}/{timestamp}/   ← generated artifacts
```

### Key design decisions

- **Demo mode vs. live mode**: If no valid `OPENAI_API_KEY` is present, the pipeline automatically falls back to pre-generated demo content from `demo_run.py`. No crashes, no empty UI — the full artifact flow runs end-to-end in demo.
- **SSE for job progress**: Artifact generation is blocking (PDF rendering, voice synthesis). The API offloads it to a thread pool and streams real-time step updates (`letter → running → done`, etc.) back to the browser via Server-Sent Events.
- **Single-file SPA**: The entire frontend lives in `static/index.html` — no build step, no bundler. Pure HTML/CSS/JS served directly from FastAPI.
- **Flat-file persistence**: Patient data is stored as JSON files under `data/`. No database dependency, easy to inspect and demo.

---

## How it works

```
Phase 1 — Family onboards once (web UI)
    ↓
    Submits profile, memories, photos, voice sample
    ↓
Phase 2 — Agent builds the memory map
    ↓
    GPT-4o reads everything, structures relationships,
    emotional anchors, recurring themes
    ↓
Phase 3 — Caregiver sees a lucid moment, taps "Lucid Moment Now"
    ↓
Phase 4 — Four artifacts generate sequentially (< 60 seconds)
    ↓
    Letter · Voice · Photo story · Dialogue guide
    ↓
Phase 5 — Caregiver downloads and delivers artifacts at bedside
```

---

## Quick start

### 1. Install

```bash
git clone https://github.com/yourusername/hearth.git
cd hearth
pip install -r requirements.txt
```

### 2. Set API keys

```bash
cp .env.example .env
# Edit .env and add your keys
```

```env
OPENAI_API_KEY=sk-...          # required for live generation
ELEVENLABS_API_KEY=...         # optional — voice cloning; falls back to TTS script if missing
```

### 3. Start the app

```bash
python app.py
# or: uvicorn app:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

### 4. Try the demo (no API key needed)

Click **"Load Demo Patient"** in the web UI — this creates Margaret Chen with five pre-loaded family memories. Then click **"Lucid Moment Now"** to generate all four artifacts using pre-generated demo content (no API call required).

---

## Project structure

```
hearth/
├── app.py                     # FastAPI web server + REST API + SSE endpoints
├── agent.py                   # GPT-4o artifact generation engine
├── memory_bank.py             # Patient data storage and retrieval (JSON flat files)
├── demo_run.py                # Pre-generated demo content (runs without API key)
├── voice_generator.py         # ElevenLabs voice synthesis / TTS fallback
├── letter_generator.py        # PDF letter generation (fpdf2)
├── photo_story.py             # Captioned photo story PDF
├── dialogue_guide.py          # Caregiver dialogue script PDF
├── main.py                    # Legacy CLI entry point (onboard / lucid_now)
├── create_patients.py         # Script to bulk-create patient records
├── build_pitch_deck.py        # Pitch deck generation utility
├── static/
│   └── index.html             # Single-page app (HTML + CSS + JS, no build step)
├── data/
│   ├── patients/              # Per-patient profiles, memories, photos, voice samples
│   └── outputs/               # Generated artifacts organized by patient + timestamp
└── sample_data/
    └── setup_demo.py          # Creates fictional demo patient Margaret Chen
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Web server | **FastAPI** + **Uvicorn** |
| Frontend | Vanilla HTML/CSS/JS SPA (no framework, no build step) |
| AI generation | **OpenAI GPT-4o** — letter, voice script, photo captions, dialogue guide |
| Voice synthesis | **ElevenLabs** voice cloning from short samples |
| PDF generation | **fpdf2** |
| Image handling | **Pillow** |
| Data store | JSON flat files (`data/`) |
| Async jobs | Python `ThreadPoolExecutor` + Server-Sent Events |
| Config | **python-dotenv** |

---

## The agent

`agent.py` wraps GPT-4o with a focused system prompt and four artifact-specific sub-prompts:

> *You are Hearth, a compassionate AI designed to help Alzheimer's patients feel connected to their families during lucid moments. You have deep knowledge of dementia care best practices. You generate artifacts that are warm, specific, simple, and grounded in real shared memories. You never use medical language. You never reference the disease. You speak only in warmth and memory. Every word you generate should make the patient feel loved and safe.*

Each artifact has its own sub-prompt tuned for tone, length, and purpose:

| Artifact | Model instruction |
|---|---|
| Letter | ~200 words, first person as family member, specific memories, no salutation |
| Voice script | 60–80 words exactly, natural spoken language, 1–2 concrete memories |
| Photo captions | 2–3 sentences per photo, second person to patient, read-aloud friendly |
| Dialogue guide | Structured JSON: opening · 5 memory prompts · photo sequence · if-distressed · closing |

### Caretaker chat

A separate streaming endpoint (`POST /api/chat/stream`) powers an always-on caretaker AI assistant in the UI. It is scoped to dementia care only — it declines unrelated questions, references the current patient's profile and memories, and streams tokens via SSE.

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/patients` | List all patients |
| `POST` | `/api/patients` | Create patient profile |
| `GET` | `/api/patients/{id}` | Full patient detail + artifact history |
| `PUT` | `/api/patients/{id}/profile` | Update profile fields |
| `DELETE` | `/api/patients/{id}` | Delete patient + all artifacts |
| `POST` | `/api/patients/{id}/memories` | Add a family memory |
| `POST` | `/api/patients/{id}/upload_photo` | Upload a photo |
| `POST` | `/api/patients/{id}/upload_voice` | Upload a voice sample |
| `POST` | `/api/patients/{id}/lucid_now` | Trigger artifact generation → returns `job_id` |
| `GET` | `/api/jobs/{job_id}` | Poll job status |
| `GET` | `/api/jobs/{job_id}/stream` | SSE stream of live job progress |
| `POST` | `/api/chat/stream` | SSE caretaker AI chat |
| `POST` | `/api/demo/setup` | Load demo patient (Margaret Chen) |
| `GET` | `/api/status` | Check if live API is available |
| `GET` | `/api/files/{patient}/{ts}/{file}` | Download generated artifact |
| `GET` | `/api/photos/{patient}/{file}` | Serve patient photo |

---

## Design principles

- **The family's love is already there.** Hearth doesn't invent feelings — it surfaces what the family has already given.
- **Never reference the disease.** The letter doesn't say "I know you're struggling." It says "I was thinking about Sunday cooking."
- **Specificity over sentiment.** "Grandma Rose's brisket recipe" lands. "I love you" by itself doesn't.
- **The caregiver is the messenger, not the author.** Every artifact is designed for a caregiver to deliver naturally in a calm room.
- **Accessibility first.** Large fonts, simple language, clear structure. A caregiver under time pressure shouldn't have to decode anything.
- **Zero-crash demo.** The full pipeline runs without any API key. Caregivers and stakeholders can see every artifact type before committing to setup.

---

## Ethical considerations

Hearth generates content in a family member's voice and name. This is a meaningful design choice and deserves care:

- **Consent.** The family member whose voice is cloned must consent explicitly to synthesized utterances being played to the patient on their behalf.
- **Review.** In production, generated artifacts should be reviewable by the family before delivery where time permits.
- **Clinical validation.** Reminiscence therapy has a research base; AI-generated reminiscence content does not yet. Real deployment would require clinician partnership and outcome measurement.
- **Scope.** Hearth is a companion, not a treatment. It supplements human caregivers; it does not replace them.

This repo is a course project and a working prototype — not a deployed clinical product.

---

## Roadmap

- [x] Four-artifact generation pipeline (letter, voice, photo story, dialogue guide)
- [x] Web interface for caregivers
- [x] Demo mode (no API key required)
- [x] Real-time SSE job progress in the browser
- [x] Caretaker AI chat assistant (scoped to dementia care)
- [x] Photo and voice file upload
- [ ] Family review queue before artifact delivery
- [ ] Multi-family-member voice support (multiple children, grandchildren)
- [ ] Memory map visualization (show the agent's internal reasoning)
- [ ] Longitudinal tracking of which artifacts land best for each patient
- [ ] Clinical validation pilot with a care facility

---

## License

MIT — see `LICENSE`.

---

## Acknowledgments

Built for an agentic AI course. The problem framing comes from hundreds of thousands of families who sit by a phone waiting for a call that comes too late. Hearth exists for them.
