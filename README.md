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
| 📄 **Letter** | A written letter in the family member's voice, referencing real shared memories. As if they wrote it this morning. |
| 🎙️ **Voice message** | A short audio message synthesized in the family member's actual cloned voice (via ElevenLabs). |
| 🖼️ **Photo story** | Family photos with warm captions the caregiver reads aloud while showing the patient. |
| 💬 **Dialogue guide** | A caregiver script — how to open, what to ask, what to show, how to respond if the patient gets anxious, how to close gently. |

The family's love is already there, waiting. The caregiver just delivers it.

---

## How it works

```
Phase 1 — Family onboards once
    ↓
    Submits voice sample, photos, memories, relationships
    ↓
Phase 2 — Agent builds the memory map
    ↓
    Claude reads everything, structures relationships, emotional anchors, recurring themes
    ↓
Phase 3 — Caregiver sees a lucid moment, taps "lucid_now"
    ↓
Phase 4 — Four artifacts generate in parallel (< 60 seconds)
    ↓
    Letter · Voice · Photo story · Dialogue guide
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

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_claude_api_key
ELEVENLABS_API_KEY=your_elevenlabs_key   # optional — voice artifact skipped if missing
```

### 3. Run the demo

```bash
python sample_data/setup_demo.py           # creates fictional patient Margaret Chen
python main.py lucid_now --patient margaret_chen
```

All four artifacts are generated and saved to `data/outputs/margaret_chen/[timestamp]/`.

---

## Usage

### Onboarding a new patient

```bash
python main.py onboard --patient margaret_chen
```

Interactive CLI walks the family member through:
- Name and relationship to patient
- Up to 10 freeform memories
- Photo file paths (copied into the patient's folder)
- A voice sample (60 seconds is enough)

Saved to `data/patients/margaret_chen/profile.json` and `memories.json`.

### Triggering a lucid moment

```bash
python main.py lucid_now --patient margaret_chen
```

Loads the patient's memory bank, calls the agent, generates all four artifacts simultaneously, and writes them to `data/outputs/[patient]/[timestamp]/`.

---

## Project structure

```
hearth/
├── main.py                    # CLI entry point (onboard / lucid_now)
├── agent.py                   # Claude-powered generation agent
├── memory_bank.py             # Patient memory storage and retrieval
├── voice_generator.py         # ElevenLabs voice synthesis
├── letter_generator.py        # PDF letter generation (fpdf2)
├── photo_story.py             # Captioned photo story PDF
├── dialogue_guide.py          # Caregiver dialogue script PDF
├── data/
│   ├── patients/              # Per-patient profiles and memories
│   └── outputs/               # Generated artifacts (timestamped)
└── sample_data/
    └── setup_demo.py          # Creates fictional demo patient
```

---

## Tech stack

- **Python 3** — application runtime
- **Anthropic Claude** — the agent brain; reads memories, reasons about what matters, generates every artifact
- **ElevenLabs** — voice cloning and synthesis from short voice samples
- **fpdf2** — PDF generation for letter, photo story, and dialogue guide
- **Pillow** — image handling for the photo story
- **python-dotenv** — API key management

---

## The agent

Hearth's system prompt:

> *You are Hearth, a compassionate AI designed to help Alzheimer's patients feel connected to their families during lucid moments. You have deep knowledge of dementia care best practices. You generate artifacts that are warm, specific, simple, and grounded in real shared memories. You never use medical language. You never reference the disease. You speak only in warmth and memory. Every word you generate should make the patient feel loved and safe.*

Each artifact has its own sub-prompt tuned for tone, length, and purpose — the letter is 200 words in first person, the voice script is 60–80 words, photo captions are 2–3 sentences each at 18pt minimum for accessibility, and the dialogue guide is structured for a caregiver to hold in their hand.

---

## Design principles

- **The family's love is already there.** Hearth doesn't invent feelings — it surfaces what the family has already given.
- **Never reference the disease.** The letter doesn't say "I know you're struggling." It says "I was thinking about Sunday cooking."
- **Specificity over sentiment.** "Grandma Rose's brisket recipe" lands. "I love you" by itself doesn't.
- **The caregiver is the messenger, not the author.** Every artifact is designed for a caregiver to deliver naturally in a calm room.
- **Accessibility first.** Large fonts, simple language, clear structure. A caregiver under time pressure shouldn't have to decode anything.

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

- [ ] Web interface for caregivers (currently CLI-only)
- [ ] Family review queue before artifact delivery
- [ ] Memory map visualization (show the agent's internal reasoning)
- [ ] Multi-family-member voice support (multiple children, grandchildren)
- [ ] Longitudinal tracking of which artifacts land best for each patient
- [ ] Clinical validation pilot with a care facility

---

## License

MIT — see `LICENSE`.

---

## Acknowledgments

Built for an agentic AI course. The problem framing comes from hundreds of thousands of families who sit by a phone waiting for a call that comes too late. Hearth exists for them.
