# Hearth

> An AI memory companion for Alzheimer's patients in care homes. When a lucid moment happens, Hearth brings the family into the room — a personal letter, a voice message, a photo story, and a caregiver script, all generated in under a minute from memories the family submitted.

---

## The problem

Alzheimer's patients experience unpredictable **lucid moments** — short windows, sometimes 20 minutes, sometimes 2 hours, where they feel like themselves again. Nobody knows when they'll happen. Families are almost never there when they do. The caregiver witnesses it alone and has nothing personal to give the patient. The moment passes. It may not come back for weeks.

You can't schedule a lucid moment. You can only be ready for one.

---

## What Hearth does

Family members submit memories **once**, from anywhere — photos, stories, relationships. Hearth reads everything and builds a memory map of the person's life before the disease.

When a lucid moment happens, the caregiver taps one button. In under 60 seconds, Hearth generates four personal artifacts from the family's real memories:

| Artifact | What it is |
|---|---|
| **Written Letter** | A ~200-word letter in the family member's voice, referencing real shared memories, rendered as a parchment-style PDF. |
| **Voice Message** | A 60–80 word script synthesized into audio using ElevenLabs TTS. Caregiver can also play it aloud directly in the browser via the Read Aloud button. |
| **Photo Story** | Family photos with warm AI-generated captions (18pt minimum) rendered as a parchment-style PDF. |
| **Dialogue Guide** | A structured caregiver script — opening, 5 memory prompts, photo sequence, distress protocol, and closing — as a parchment-style PDF. |

The family's love is already there, waiting. The caregiver just delivers it.

---

## Architecture

```
Browser (SPA — static/index.html)
    │
    │  HTTP / Server-Sent Events
    ▼
FastAPI (app.py — port 8000)
    │
    ├── GET  /                           → serves index.html SPA
    ├── GET  /api/status                 → check if OpenAI API is reachable
    │
    ├── GET  /api/patients               → list all patients
    ├── POST /api/patients               → create patient profile
    ├── GET  /api/patients/{id}          → patient detail + artifact history
    ├── PUT  /api/patients/{id}/profile  → update profile fields
    ├── DELETE /api/patients/{id}        → delete patient + all outputs
    ├── POST /api/patients/{id}/memories → add a family memory
    ├── POST /api/patients/{id}/upload_photo
    ├── POST /api/patients/{id}/upload_voice
    │
    ├── POST /api/patients/{id}/lucid_now → enqueue job → returns job_id
    ├── GET  /api/jobs/{job_id}           → poll job status
    ├── GET  /api/jobs/{job_id}/stream    → SSE real-time step progress
    │
    ├── POST /api/tts                     → ElevenLabs TTS (powers Read Aloud button)
    ├── POST /api/chat/stream             → SSE caretaker AI chat (GPT-4o, scoped)
    ├── POST /api/demo/setup              → create demo patient Margaret Chen
    │
    ├── GET  /api/files/{patient}/{ts}/{file} → serve generated artifact
    └── GET  /api/photos/{patient}/{file}     → serve patient photo
    │
    ├── ThreadPoolExecutor (4 workers)
    │       └── _run_lucid_now()
    │               ├── HearthAgent.generate_letter()         → letter_generator.py  → PDF
    │               ├── HearthAgent.generate_voice_script()   → voice_generator.py   → MP3 or TXT
    │               ├── HearthAgent.generate_photo_captions() → photo_story.py       → PDF
    │               └── HearthAgent.generate_dialogue_guide() → dialogue_guide.py    → PDF
    │
    └── memory_bank.py  (JSON flat-file store)
            data/patients/{id}/profile.json
            data/patients/{id}/memories.json
            data/patients/{id}/photos/
            data/patients/{id}/voice_samples/
            data/outputs/{id}/{timestamp}/    ← generated artifacts
```

### Key design decisions

- **Demo mode vs. live mode** — If no valid `OPENAI_API_KEY` is present, the pipeline falls back to pre-generated content from `demo_run.py`. No crashes, no empty UI.
- **SSE for job progress** — Artifact generation is blocking (PDF rendering, API calls). The API offloads it to a thread pool and streams real-time step-level updates back via Server-Sent Events.
- **ElevenLabs via REST, not SDK** — The `/api/tts` endpoint calls the ElevenLabs REST API directly using `httpx` (already a FastAPI dependency). This avoids the `elevenlabs` Python package entirely, which has a Windows long-path install bug.
- **Single-file SPA** — The entire frontend lives in `static/index.html`. No build step, no bundler, no Node.js required.
- **Flat-file persistence** — Patient data is stored as JSON files under `data/`. No database dependency, trivial to inspect and demo.

---

## How it works

```
Phase 1 — Family onboards once (web UI)
    ↓
    Submits profile, memories, photos
    ↓
Phase 2 — Agent builds the memory map
    ↓
    GPT-4o reads all memories, structures relationships,
    emotional anchors, recurring themes
    ↓
Phase 3 — Caregiver sees a lucid moment → taps "Lucid Moment Now"
    ↓
Phase 4 — Four artifacts generate (< 60 seconds)
    ↓
    Letter (PDF)  ·  Voice (MP3)  ·  Photo Story (PDF)  ·  Dialogue Guide (PDF)
    ↓
Phase 5 — Caregiver downloads, plays audio in browser, delivers at bedside
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
```

Edit `.env`:

```env
OPENAI_API_KEY=sk-...          # required — artifact text generation + caretaker chat
ELEVENLABS_API_KEY=...         # required — voice MP3 generation + Read Aloud button
```

### 3. Start the app

```bash
python app.py
```

Open **http://localhost:8000** in your browser.

### 4. Try the demo (no API keys needed)

Click **"Load Demo Patient"** in the web UI to create Margaret Chen with five pre-loaded family memories. Then click **"Lucid Moment Now"** — all four artifacts generate using pre-built demo content, no API call required.

---

## Project structure

```
hearth/
├── app.py                  # FastAPI server — REST API, SSE endpoints, /api/tts
├── agent.py                # GPT-4o artifact generation (letter, voice, captions, guide)
├── memory_bank.py          # Patient data storage and retrieval (JSON flat files)
├── demo_run.py             # Pre-generated demo content (no API key required)
├── voice_generator.py      # ElevenLabs voice synthesis via SDK; text fallback
├── letter_generator.py     # Parchment-style PDF letter (fpdf2, Times font)
├── photo_story.py          # Parchment-style captioned photo story PDF
├── dialogue_guide.py       # Parchment-style caregiver dialogue script PDF
├── main.py                 # Legacy CLI entry point (onboard / lucid_now)
├── create_patients.py      # Bulk patient record creation script
├── build_pitch_deck.py     # Pitch deck generation utility
├── static/
│   └── index.html          # Full SPA — HTML + CSS + JS, no build step
├── data/
│   ├── patients/           # Per-patient profiles, memories, photos, voice samples
│   └── outputs/            # Generated artifacts by patient + timestamp
├── sample_data/
│   └── setup_demo.py       # Creates fictional demo patient Margaret Chen
├── .env                    # API keys (not committed)
└── requirements.txt
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Web server | **FastAPI** + **Uvicorn** |
| Frontend | Vanilla HTML/CSS/JS SPA — no framework, no build step |
| AI — text generation | **OpenAI GPT-4o** via `openai` SDK |
| AI — caretaker chat | **OpenAI GPT-4o** streaming via SSE, scoped to dementia care |
| Voice synthesis (artifact) | **ElevenLabs** via `elevenlabs` SDK — voice ID `pFZP5JQG7iQjIQuC4Bku` |
| Voice synthesis (Read Aloud) | **ElevenLabs REST API** via `httpx` — same voice ID, no SDK needed |
| PDF generation | **fpdf2** — Times New Roman, parchment background, amber double border |
| Image handling | **Pillow** |
| HTTP client | **httpx** (bundled with FastAPI) |
| Data store | JSON flat files (`data/`) |
| Async job processing | Python `ThreadPoolExecutor` + Server-Sent Events |
| Config | **python-dotenv** |

---

## ElevenLabs integration

ElevenLabs is used in two distinct places:

### 1. Artifact generation (`voice_generator.py`)

When **Lucid Moment Now** is triggered, `voice_generator.py` uses the `elevenlabs` SDK to synthesize the GPT-4o-generated voice script into an MP3:

```python
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
response = client.text_to_speech.convert(voice_id="pFZP5JQG7iQjIQuC4Bku", text=script)
```

If `ELEVENLABS_API_KEY` is not set or synthesis fails, it gracefully saves the script as a `.txt` file instead and the UI displays it as readable text.

### 2. Read Aloud button (`/api/tts` in app.py)

When the voice artifact is a text script (no ElevenLabs key during generation), the **Read Aloud** button in the UI calls `POST /api/tts`. This endpoint uses `httpx` to call the ElevenLabs REST API directly — no SDK needed:

```
POST /api/tts  { "text": "..." }
→ calls https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
→ returns audio/mpeg
→ browser plays via Audio API
```

The button shows **"Loading…"** while fetching, switches to **"Stop"** during playback, and resets automatically when audio ends.

> **Note on Windows installation:** The `elevenlabs` Python package cannot be installed on Windows systems without Long Path support enabled (the package contains file paths that exceed the 260-character default limit). The `/api/tts` endpoint sidesteps this entirely by using the REST API directly via `httpx`.

---

## PDF design system

All three artifact PDFs share an identical visual design:

| Element | Spec |
|---|---|
| Background | Warm parchment `rgb(252, 245, 228)` |
| Outer border | Amber `rgb(180, 130, 60)`, 1.8pt |
| Inner border | Gold `rgb(210, 170, 100)`, 0.5pt |
| Corner accents | Filled amber ellipses at all four corners |
| Primary font | Times New Roman Bold 24pt — titles |
| Body font | Times New Roman 13pt — body text |
| Caption font | Times New Roman 18pt — photo captions (accessibility minimum) |
| Title color | `rgb(110, 70, 20)` warm brown |
| Body color | `rgb(45, 30, 15)` near-black |
| Divider | Double amber rule — thick (0.6pt) outer, thin (0.2pt) inner |
| Margins | 28mm left/right, 22mm top |

All content is fully dynamic — no hardcoded instructional text, no branding footers.

---

## The agent (`agent.py`)

Wraps GPT-4o with a focused system prompt and four artifact-specific sub-prompts:

> *You are Hearth, a compassionate AI designed to help Alzheimer's patients feel connected to their families during lucid moments. You generate artifacts that are warm, specific, simple, and grounded in real shared memories. You never use medical language. You never reference the disease. Every word you generate should make the patient feel loved and safe.*

| Artifact | Generation spec |
|---|---|
| Letter | ~200 words, first person as family member, specific real memories, no salutation |
| Voice script | 60–80 words, natural spoken language, 1–2 concrete memories |
| Photo captions | 2–3 sentences per photo, second person to patient, read-aloud friendly |
| Dialogue guide | Structured JSON: opening · 5 memory prompts · photo sequence · if-distressed · closing |

### Caretaker chat

`POST /api/chat/stream` powers a streaming AI assistant scoped exclusively to dementia care. It references the current patient's profile and memories, declines off-topic questions, and streams tokens via SSE. Powered by GPT-4o.

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
| `POST` | `/api/patients/{id}/upload_photo` | Upload a photo file |
| `POST` | `/api/patients/{id}/upload_voice` | Upload a voice sample |
| `POST` | `/api/patients/{id}/lucid_now` | Trigger generation → returns `job_id` |
| `GET` | `/api/jobs/{job_id}` | Poll job status |
| `GET` | `/api/jobs/{job_id}/stream` | SSE stream of real-time job progress |
| `POST` | `/api/tts` | ElevenLabs TTS → returns `audio/mpeg` |
| `POST` | `/api/chat/stream` | SSE caretaker AI chat |
| `POST` | `/api/demo/setup` | Create demo patient (Margaret Chen) |
| `GET` | `/api/status` | Check OpenAI API availability |
| `GET` | `/api/files/{patient}/{ts}/{file}` | Download a generated artifact |
| `GET` | `/api/photos/{patient}/{file}` | Serve a patient photo |

---

## Design principles

- **The family's love is already there.** Hearth doesn't invent feelings — it surfaces what the family has already given.
- **Never reference the disease.** The letter doesn't say "I know you're struggling." It says "I was thinking about Sunday cooking."
- **Specificity over sentiment.** "Grandma Rose's brisket recipe" lands. "I love you" by itself doesn't.
- **The caregiver is the messenger, not the author.** Every artifact is designed to be delivered naturally in a calm room.
- **Accessibility first.** Large fonts (18pt minimum for photo captions), simple language, clear structure.
- **Zero-crash demo.** The full pipeline runs without any API key — stakeholders see every artifact before committing to setup.

---

## Ethical considerations

- **Consent.** The voice used in synthesis must be authorised for this purpose. In production, explicit consent from the family member is required.
- **Review.** Generated artifacts should be reviewable by the family before delivery where time permits.
- **Clinical validation.** Reminiscence therapy has a research base; AI-generated reminiscence content does not yet. Real deployment requires clinician partnership.
- **Scope.** Hearth is a companion, not a treatment. It supplements human caregivers; it does not replace them.

This repo is a course project and a working prototype — not a deployed clinical product.

---

## Roadmap

- [x] Four-artifact generation pipeline (letter, voice, photo story, dialogue guide)
- [x] Web interface for caregivers
- [x] Demo mode (no API key required)
- [x] Real-time SSE job progress in the browser
- [x] Caretaker AI chat assistant (GPT-4o, scoped to dementia care)
- [x] Photo and voice file upload
- [x] ElevenLabs voice synthesis (artifact MP3 + Read Aloud browser button)
- [x] Parchment-style PDF design across all three artifact PDFs
- [x] All hardcoded text removed — fully dynamic content
- [ ] Family review queue before artifact delivery
- [ ] Multi-family-member voice support
- [ ] Memory map visualization
- [ ] Longitudinal tracking of which artifacts resonate most
- [ ] Clinical validation pilot with a care facility

---

## License

MIT — see `LICENSE`.

---

## Acknowledgments

Built for an agentic AI course. The problem framing comes from hundreds of thousands of families who sit by a phone waiting for a call that comes too late. Hearth exists for them.
