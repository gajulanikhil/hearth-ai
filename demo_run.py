"""
demo_run.py — Runs the full Hearth artifact pipeline with pre-generated content.

This demonstrates every artifact generator (letter, voice, photo story, dialogue guide)
without needing a live API call. Use this to verify the pipeline works, then
set OPENAI_API_KEY in .env and run:
    python main.py lucid_now --patient margaret_chen
for the live agent-driven version.
"""

import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent

import memory_bank

PATIENT_ID = "margaret_chen"

# ─────────────────────────────────────────────────────────────────────────────
# PRE-GENERATED ARTIFACT CONTENT
# (This is what the Hearth agent — gpt-4o — would produce from
#  the five memories David Chen submitted for Margaret Chen.)
# ─────────────────────────────────────────────────────────────────────────────

LETTER_TEXT = """Mom,

I've been thinking about Sunday mornings. That specific smell — garlic going in on a Saturday night, low and slow, so you'd wake up already knowing what day it was. Grandma Rose gave you the recipe but you made it yours over forty years, and I don't think you ever wrote it down because you didn't need to. It lived in your hands.

I think about Galveston too. The morning light on the Gulf — Dad said it looked like hammered tin, and you loved that phrase so much you kept it. You and him walking the pier before I was even awake. The shrimp tacos you said were the best thing you'd ever eaten, and I believe you meant it that time.

And Biscuit, who was supposed to be my dog and immediately became yours. Fourteen years. He slept on your side of the bed and you denied it every single time, and Dad just smiled.

Your garden. The marigolds enormous. The tomatoes. Standing there in the morning with your coffee, just looking.

Those mornings are still in me, Mom. All of them. I carry them the way you carry a good recipe — not written down, just known.

I love you. I'll see you soon.

David"""

VOICE_SCRIPT = """Mom, it's David. I was thinking about you today, about that Sunday morning smell — garlic going in Saturday night, you up before anyone, knowing exactly what you were doing. And I thought about Galveston, you and Dad on the pier in the morning light. He said the Gulf looked like hammered tin. You loved that. So do I. Those are good things to carry, Mom. I love you. I'll see you very soon."""

PHOTO_CAPTIONS = [
    {
        "filename": "brisket_sunday.jpg",
        "caption": "This is your Sunday table, Mom — the one with Grandma Rose's brisket that you made your own over forty years. You always put out the white embroidered tablecloth, the one from your wedding shower. You'd stand over it and say 'not too thick' every time Dad carved, and he'd smile and do it exactly his way anyway."
    },
    {
        "filename": "galveston_1987.jpg",
        "caption": "This is Galveston, 1987 — your first real vacation in years, after Dad retired. You and George walked the pier every morning before anyone else was up. He said the Gulf looked like hammered tin when the light hit it that way, and you kept that phrase for the rest of your life. You had shrimp tacos from a roadside stand and said they were the best thing you'd ever eaten."
    },
    {
        "filename": "george_margaret_anniversary.jpg",
        "caption": "This is you and George at your 40th anniversary. Fifty-two years together, and David says you talked about him like he was still in the next room — the hardware store Saturdays, the first apartment in Houston, the small ordinary things. This photo sat on your vanity where you could always see it."
    },
    {
        "filename": "garden_bellaire.jpg",
        "caption": "This is your garden on Bellaire — the marigolds enormous, the tomatoes and sweet basil along the fence. You'd go out in the morning in your house robe with a cup of coffee and just stand there looking. You said plants needed attention the way people do, and everything grew for you."
    },
    {
        "filename": "biscuit_dog.jpg",
        "caption": "This is Biscuit — he was supposed to be David's dog and immediately became yours, sleeping on your side of the bed every night for fourteen years. You'd deny it every time it came up. Dad would smile. Biscuit had the good long life of a dog who was very, very loved."
    },
]

DIALOGUE_GUIDE = {
    "opening": (
        "Margaret, good morning. It's so nice to be here with you. "
        "You're looking well today. I've been looking forward to sitting with you for a bit — "
        "I thought we might look at some photos together and just talk."
    ),
    "memory_prompts": [
        {
            "prompt": "Margaret, do you remember making brisket on Sundays? I heard you had a recipe that was really something special.",
            "why_it_works": "Sunday cooking is listed as a core emotional anchor — this has a high chance of sparking vivid, positive recall.",
            "follow_up": "Tell me about the recipe — was it your mother's, or did you make it your own?"
        },
        {
            "prompt": "Have you ever been to Galveston? I'd love to hear what the Gulf looks like from the pier.",
            "why_it_works": "The Galveston pier is a named emotional anchor. The specific detail 'hammered tin' may surface if she remembers it.",
            "follow_up": "Did you and George ever walk on the pier in the morning? I heard the light does something beautiful to the water."
        },
        {
            "prompt": "I hear you had a dog named Biscuit. Tell me about him.",
            "why_it_works": "Biscuit is a calming topic. Animal memories tend to carry strong positive affect and are often accessible even in moderate-stage dementia.",
            "follow_up": "He sounds like he was such good company. What was he like when he was young?"
        },
        {
            "prompt": "Did you have a garden? I'd love to hear what you grew.",
            "why_it_works": "The garden is a calming topic. Sensory memory — smells, textures — often stays intact longer than episodic memory.",
            "follow_up": "Marigolds — I've heard those keep the bugs away. Did you have a trick to making them grow so big?"
        },
        {
            "prompt": "Do you like Frank Sinatra? I was listening to him this morning.",
            "why_it_works": "Music memory is often preserved late into dementia. Frank Sinatra is listed as a calming topic and can anchor mood quickly.",
            "follow_up": "Did you have a favorite song of his? I'd love to know which one."
        }
    ],
    "photo_sequence": [
        {
            "photo": "brisket_sunday.jpg",
            "introduction": "Margaret, I have a photo I'd love to show you. This one is from your kitchen — your Sunday table. Do you recognize it?"
        },
        {
            "photo": "galveston_1987.jpg",
            "introduction": "And here's one from Galveston — 1987. You're on the pier with George. Look at that water behind you."
        },
        {
            "photo": "george_margaret_anniversary.jpg",
            "introduction": "This is a beautiful one — your 40th anniversary. You and George together."
        },
        {
            "photo": "garden_bellaire.jpg",
            "introduction": "Here's your garden. Those marigolds — David said they were enormous."
        },
        {
            "photo": "biscuit_dog.jpg",
            "introduction": "And this one — do you know who this is? That's Biscuit."
        }
    ],
    "if_distressed": (
        "Margaret, it's okay. You're safe, and I'm right here with you. "
        "Let's set these aside for a moment. "
        "Can you tell me about your garden — do you remember what you liked to grow? "
        "We can just sit quietly together for a bit. There's nowhere we need to be."
    ),
    "closing": (
        "Margaret, thank you for spending this time with me. "
        "It's been so lovely to hear about your family and all those beautiful places. "
        "David sends his love — he's thinking about you, and he'll see you soon."
    )
}


def run_demo() -> None:
    print()
    print("  +------------------------------------------+")
    print("  |  HEARTH -- Full Pipeline Demo            |")
    print("  |  Patient: Margaret Chen                  |")
    print("  +------------------------------------------+")
    print()

    profile = memory_bank.load_profile(PATIENT_ID)
    memories = memory_bank.load_memories(PATIENT_ID)
    photos_dir = memory_bank.get_photos_dir(PATIENT_ID)
    voice_samples_dir = memory_bank.get_voice_samples_dir(PATIENT_ID)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = ROOT / "data" / "outputs" / PATIENT_ID / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Output folder: {output_dir}")
    print()
    print("  Rendering artifacts...")
    print()

    results = {}

    # ── Artifact 1: Letter PDF ────────────────────────────────────────────────
    try:
        from letter_generator import generate_letter_pdf
        letter_path = output_dir / f"letter_{PATIENT_ID}_{timestamp}.pdf"
        generate_letter_pdf(LETTER_TEXT, profile, letter_path)
        results["letter"] = letter_path
        print(f"  [Letter PDF]       {letter_path.name}")
    except Exception as e:
        print(f"  [Letter PDF]       ERROR: {e}")
        import traceback; traceback.print_exc()

    # ── Artifact 2: Voice (text fallback — no ElevenLabs key) ────────────────
    try:
        from voice_generator import _save_text_fallback
        voice_path = output_dir / f"voice_{PATIENT_ID}_{timestamp}.mp3"
        txt_path = _save_text_fallback(VOICE_SCRIPT, voice_path, profile["primary_family_contact"])
        results["voice"] = txt_path
        print(f"  [Voice Script]     {txt_path.name}")
    except Exception as e:
        print(f"  [Voice Script]     ERROR: {e}")
        import traceback; traceback.print_exc()

    # ── Artifact 3: Photo Story PDF ───────────────────────────────────────────
    try:
        from photo_story import generate_photo_story_pdf
        story_path = output_dir / f"photo_story_{PATIENT_ID}_{timestamp}.pdf"
        generate_photo_story_pdf(PHOTO_CAPTIONS, profile, photos_dir, story_path)
        results["photo_story"] = story_path
        print(f"  [Photo Story PDF]  {story_path.name}")
    except Exception as e:
        print(f"  [Photo Story PDF]  ERROR: {e}")
        import traceback; traceback.print_exc()

    # ── Artifact 4: Dialogue Guide PDF ────────────────────────────────────────
    try:
        from dialogue_guide import generate_dialogue_guide_pdf
        guide_path = output_dir / f"dialogue_guide_{PATIENT_ID}_{timestamp}.pdf"
        generate_dialogue_guide_pdf(DIALOGUE_GUIDE, profile, guide_path)
        results["dialogue_guide"] = guide_path
        print(f"  [Dialogue Guide]   {guide_path.name}")
    except Exception as e:
        print(f"  [Dialogue Guide]   ERROR: {e}")
        import traceback; traceback.print_exc()

    print()
    print("  " + "-" * 44)
    print(f"  Artifacts ready. Lucid moment package saved.")
    print(f"  {len(results)} artifact(s) generated successfully.")
    print()
    print("  Files:")
    for key, path in results.items():
        print(f"    {path}")
    print()
    print("  To run with live OpenAI API:")
    print("    1. Add OPENAI_API_KEY to .env")
    print("    2. python main.py lucid_now --patient margaret_chen")
    print()


if __name__ == "__main__":
    run_demo()
