"""
sample_data/setup_demo.py — Creates a complete fictional demo patient.

Populates Margaret Chen (79, moderate Alzheimer's) with:
- A rich patient profile
- 5 detailed memories from her son David
- 3 placeholder photo descriptions
- A voice script placeholder

Run this once before running:
    python main.py lucid_now --patient margaret_chen
"""

import json
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Resolve project root (one level up from sample_data/)
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import memory_bank

PATIENT_ID = "margaret_chen"


def create_demo() -> None:
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║      HEARTH — Demo Setup: Margaret Chen  ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    # ── Patient Profile ──────────────────────────────────────────────────────
    profile = {
        "name": "Margaret Chen",
        "age": 79,
        "stage": "moderate",
        "primary_family_contact": "David Chen (son)",
        "emotional_anchors": [
            "Sunday cooking",
            "Galveston pier",
            "late husband George",
        ],
        "calming_topics": [
            "garden",
            "her dog Biscuit",
            "Frank Sinatra music",
        ],
        "avoid_topics": [
            "her sister's death",
            "the accident",
        ],
        "current_mood_baseline": "gentle, sometimes anxious in late afternoon",
        "best_time_of_day": "mid-morning",
    }

    memory_bank.save_profile(PATIENT_ID, profile)
    print(f"  Profile created: {profile['name']}, {profile['age']}")

    # ── Memories from David ──────────────────────────────────────────────────
    memories = [
        {
            "submitted_by": "David Chen",
            "relationship": "son",
            "memory_text": (
                "Mom used to make brisket every Sunday. She said it was Grandma Rose's recipe, "
                "though she'd tweaked it over forty years until it was really hers. She'd start it "
                "Saturday night — you could smell the garlic and bay leaves from my bedroom. By Sunday "
                "morning the whole house smelled like it. She'd say, 'David, go set the table,' and that "
                "meant we were almost there. She always used the white tablecloth with the embroidered "
                "edges, the one she got at her wedding shower. She was very particular about that tablecloth. "
                "Dad would carve and she'd hover. 'Not too thick,' she'd say, every single time. "
                "I've tried to make it three times. I can't get it right. I don't think anyone ever will."
            ),
            "associated_photos": ["brisket_sunday.jpg"],
            "emotional_tone": "warm",
            "voice_sample_file": "david_voice_sample.mp3",
        },
        {
            "submitted_by": "David Chen",
            "relationship": "son",
            "memory_text": (
                "The Galveston trip was 1987. Dad had just retired — first real vacation they'd taken "
                "in maybe ten years. I was twelve. We drove down in the station wagon and Mom sang "
                "along to the radio the whole way, every song, even the ones she pretended she didn't know. "
                "We stayed at a little motel a block from the seawall. Mom and Dad walked out on the pier "
                "every morning before I was even awake. She told me later that Dad said the Gulf looked like "
                "'hammered tin' when the light hit it a certain way. She loved that phrase. She repeated it "
                "for years. 'Hammered tin.' We ate shrimp tacos from a roadside stand and she said they were "
                "the best thing she'd ever eaten. She said that a lot, but that time I think she meant it."
            ),
            "associated_photos": ["galveston_1987.jpg"],
            "emotional_tone": "warm",
            "voice_sample_file": "david_voice_sample.mp3",
        },
        {
            "submitted_by": "David Chen",
            "relationship": "son",
            "memory_text": (
                "Dad — George — died in 2009. They were married 52 years. She kept his cardigan on the "
                "back of the bedroom chair for about three years after. She said it still smelled like him, "
                "though I'm not sure that was literally true anymore. She didn't talk about him being gone. "
                "She talked about him being there — stories from when they were young, from their first "
                "apartment in Houston, from the Saturday afternoons they'd spend at the hardware store "
                "because Dad liked looking at tools even when he didn't need them. She kept a photo of "
                "them at their 40th anniversary party on her vanity. She still talks to it sometimes. "
                "I pretend not to notice. I think it helps her."
            ),
            "associated_photos": ["george_margaret_anniversary.jpg"],
            "emotional_tone": "bittersweet",
            "voice_sample_file": "david_voice_sample.mp3",
        },
        {
            "submitted_by": "David Chen",
            "relationship": "son",
            "memory_text": (
                "Mom had a garden in the backyard of the house on Bellaire. Not a big garden — just "
                "a strip along the fence — but she was obsessive about it. Tomatoes, zucchini, sweet "
                "basil, and always a row of marigolds she said kept the bugs off. She'd go out in the "
                "morning in her house robe and flip-flops with a cup of coffee and just stand there "
                "looking at it. Not doing anything. Just looking. She said plants needed you to pay "
                "attention to them the way people do. I never knew if she really believed that or if "
                "it was just an excuse to have quiet time. She had a green thumb, genuinely. Everything "
                "grew for her. The marigolds were enormous. She'd bring bunches of them inside and "
                "put them in a mason jar on the kitchen windowsill."
            ),
            "associated_photos": ["garden_bellaire.jpg"],
            "emotional_tone": "warm",
            "voice_sample_file": "david_voice_sample.mp3",
        },
        {
            "submitted_by": "David Chen",
            "relationship": "son",
            "memory_text": (
                "Biscuit was a beagle mix we got when I was eight, in 1983. Mom said the dog was "
                "mine and my responsibility, but within a week she was the one feeding him and he "
                "slept on her side of the bed. She'd deny this every time it came up. Dad would "
                "smile and say nothing. Biscuit lived to fourteen — a good long life for a dog that "
                "ate table scraps every single meal. When he died Mom cried harder than I'd ever "
                "seen her cry over anything. She kept his collar in her jewelry box. I found it "
                "when we were packing up the house — red nylon, with a little bone-shaped tag. "
                "She lit up when I told her about Biscuit last month. She said, 'He was such a "
                "good dog,' and she smiled the way she used to. That one memory still gets through."
            ),
            "associated_photos": ["biscuit_dog.jpg"],
            "emotional_tone": "warm",
            "voice_sample_file": "david_voice_sample.mp3",
        },
    ]

    memory_bank.save_memories(PATIENT_ID, memories)
    print(f"  Memories saved: {len(memories)}")

    # ── Placeholder photos (descriptions only — no real image files) ─────────
    # Create a note file so the user knows what photos are expected
    photos_dir = memory_bank.get_photos_dir(PATIENT_ID)
    photo_notes = {
        "brisket_sunday.jpg": "Margaret at the Sunday table, carving brisket. George in the background. Bellaire house kitchen, circa 1990.",
        "galveston_1987.jpg": "Margaret and George on the Galveston pier. Young David in the foreground. Gulf of Mexico behind them.",
        "george_margaret_anniversary.jpg": "George and Margaret at their 40th wedding anniversary party, 1997. They're dancing.",
        "garden_bellaire.jpg": "Margaret in her garden. Morning light. House robe. Coffee cup in one hand. Marigolds in bloom.",
        "biscuit_dog.jpg": "Biscuit the beagle asleep on the couch. Margaret's hand in frame, scratching his ear.",
    }

    notes_path = photos_dir / "README_photos.txt"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("HEARTH — PHOTO PLACEHOLDERS FOR MARGARET CHEN\n")
        f.write("=" * 50 + "\n\n")
        f.write("These photos are referenced in the memory bank but not included.\n")
        f.write("Place actual photos in this directory with these exact filenames,\n")
        f.write("or the photo story will show placeholder boxes instead.\n\n")
        for filename, description in photo_notes.items():
            f.write(f"{filename}\n  {description}\n\n")

    print(f"  Photo placeholder notes: {notes_path.name}")

    # Create simple placeholder image files using Pillow (so photo story works without real photos)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        print("  Creating placeholder images with Pillow...")
        for filename, description in photo_notes.items():
            img_path = photos_dir / filename
            if not img_path.exists():
                # Create a warm-toned placeholder
                img = Image.new("RGB", (800, 600), color=(245, 235, 220))
                draw = ImageDraw.Draw(img)

                # Border
                draw.rectangle([10, 10, 789, 589], outline=(180, 150, 120), width=3)

                # Camera icon (simple)
                draw.ellipse([360, 200, 440, 280], outline=(160, 130, 100), width=4)
                draw.rectangle([330, 210, 470, 290], outline=(160, 130, 100), width=2)

                # Filename label
                draw.text(
                    (400, 330),
                    filename,
                    fill=(120, 90, 60),
                    anchor="mm",
                )

                # Description (wrapped)
                wrapped = textwrap.fill(description, width=60)
                y_start = 370
                for line in wrapped.split("\n"):
                    draw.text(
                        (400, y_start),
                        line,
                        fill=(100, 75, 50),
                        anchor="mm",
                    )
                    y_start += 22

                draw.text(
                    (400, 540),
                    "[ placeholder — replace with real photo ]",
                    fill=(180, 155, 130),
                    anchor="mm",
                )

                img.save(str(img_path), "JPEG", quality=85)
                print(f"    Created: {filename}")

    except ImportError:
        print("  Pillow not installed — placeholder images not created.")
        print("  Photo story will show empty boxes without real photos.")
    except Exception as e:
        print(f"  Warning creating placeholder images: {e}")

    # ── Voice sample placeholder ─────────────────────────────────────────────
    voice_dir = memory_bank.get_voice_samples_dir(PATIENT_ID)
    voice_note_path = voice_dir / "README_voice.txt"
    with open(voice_note_path, "w", encoding="utf-8") as f:
        f.write("HEARTH — VOICE SAMPLE PLACEHOLDER FOR MARGARET CHEN\n")
        f.write("=" * 50 + "\n\n")
        f.write("Expected file: david_voice_sample.mp3\n\n")
        f.write("This should be a 30-60 second recording of David Chen\n")
        f.write("speaking naturally (reading aloud, having a conversation, etc).\n\n")
        f.write("Without this file:\n")
        f.write("  - The voice message will be saved as a .txt script instead of .mp3\n")
        f.write("  - All other artifacts (letter, photo story, dialogue guide) are unaffected.\n\n")
        f.write("SAMPLE SCRIPT (60-80 words David could record):\n")
        f.write("-" * 40 + "\n")
        f.write(
            "Mom, it's David. I was thinking about you today. I thought about that Sunday "
            "brisket smell — the garlic starting on Saturday night, waking up on Sunday morning "
            "and knowing. Nobody makes it like you. And I thought about Galveston — you and Dad "
            "on the pier, the Gulf all silver in the morning. Those are good things to carry. "
            "I love you, Mom. I'll see you soon.\n"
        )

    print(f"  Voice sample notes: {voice_note_path.name}")

    # ── Done ─────────────────────────────────────────────────────────────────
    print()
    print("  Demo setup complete.")
    print()
    print("  Patient:      Margaret Chen, 79")
    print("  Memories:     5 (from David Chen, son)")
    print("  Photos:       5 placeholder images (or descriptions if Pillow unavailable)")
    print("  Voice sample: placeholder notes only (no real voice file)")
    print()
    print("  Next step:")
    print("    python main.py lucid_now --patient margaret_chen")
    print()


if __name__ == "__main__":
    create_demo()
