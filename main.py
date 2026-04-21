"""
main.py — Hearth CLI entry point.

Two modes:
  python main.py onboard --patient <patient_id>
      Interactive walkthrough for a family member to submit memories.

  python main.py lucid_now --patient <patient_id>
      Triggers artifact generation when a lucid moment is happening.
"""

import argparse
import os
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

# Resolve project root so this works from any working directory
ROOT = Path(__file__).parent

import memory_bank
from agent import HearthAgent


# ─────────────────────────────────────────────────────────────────────────────
# MODE 1: ONBOARD
# ─────────────────────────────────────────────────────────────────────────────

def run_onboard(patient_id: str) -> None:
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║        HEARTH — Family Onboarding        ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print("  Thank you for taking the time to share your memories.")
    print("  Everything you share here will be used to create personal")
    print("  artifacts for your loved one during lucid moments.")
    print()

    # ── Family member info ───────────────────────────────────────────────────
    submitted_by = input("  Your full name: ").strip()
    relationship = input("  Your relationship to the patient (e.g., son, daughter): ").strip()
    print()

    # ── Patient profile ──────────────────────────────────────────────────────
    if memory_bank.patient_exists(patient_id):
        profile = memory_bank.load_profile(patient_id)
        print(f"  Found existing profile for: {profile['name']}")
        print(f"  Adding memories from {submitted_by} ({relationship}).")
    else:
        print("  No existing profile found. Let's create one.")
        print()
        patient_name = input("  Patient's full name: ").strip()
        age = input("  Patient's age: ").strip()
        stage = input("  Dementia stage (mild/moderate/severe): ").strip() or "moderate"
        print()
        print("  Emotional anchors are memories/themes that make them light up.")
        anchors_raw = input("  Emotional anchors (comma-separated, e.g. 'Sunday cooking, Galveston pier'): ").strip()
        emotional_anchors = [a.strip() for a in anchors_raw.split(",") if a.strip()]

        calming_raw = input("  Calming topics if anxious (comma-separated): ").strip()
        calming_topics = [a.strip() for a in calming_raw.split(",") if a.strip()]

        avoid_raw = input("  Topics to avoid (comma-separated): ").strip()
        avoid_topics = [a.strip() for a in avoid_raw.split(",") if a.strip()]

        mood = input("  Current mood baseline (e.g. 'gentle, sometimes anxious in late afternoon'): ").strip()
        best_time = input("  Best time of day for visits (e.g. 'mid-morning'): ").strip()

        profile = {
            "name": patient_name,
            "age": int(age) if age.isdigit() else age,
            "stage": stage,
            "primary_family_contact": f"{submitted_by} ({relationship})",
            "emotional_anchors": emotional_anchors,
            "calming_topics": calming_topics,
            "avoid_topics": avoid_topics,
            "current_mood_baseline": mood,
            "best_time_of_day": best_time,
        }
        memory_bank.save_profile(patient_id, profile)
        print(f"\n  Profile created for {patient_name}.")

    # ── Memory collection ────────────────────────────────────────────────────
    print()
    print("  ─" * 22)
    print(f"  Now let's collect your memories. You can share up to 10.")
    print("  Be as specific as you can — real names, real places, real details.")
    print("  ─" * 22)
    print()

    new_memories = []
    for i in range(1, 11):
        print(f"  Memory {i} of 10 (press Enter with no text to stop):")
        memory_text = input("    > ").strip()
        if not memory_text:
            print("  Stopping memory collection.")
            break

        # Photos for this memory
        photos = []
        print("  Any photo filenames associated with this memory?")
        print("  Enter file paths one per line (press Enter with no path to skip):")
        while True:
            photo_path = input("    Photo path: ").strip()
            if not photo_path:
                break
            filename = memory_bank.copy_photo(patient_id, photo_path)
            if filename:
                photos.append(filename)
                print(f"    Copied: {filename}")

        tone = input("  Emotional tone of this memory (warm/bittersweet/joyful/nostalgic) [warm]: ").strip() or "warm"

        new_memories.append({
            "submitted_by": submitted_by,
            "relationship": relationship,
            "memory_text": memory_text,
            "associated_photos": photos,
            "emotional_tone": tone,
        })
        print()

    # ── Voice sample ─────────────────────────────────────────────────────────
    print("  ─" * 22)
    print("  Voice sample (optional but recommended).")
    print("  A 30-60 second recording of you speaking normally is enough.")
    print("  This is used to synthesize a voice message in your voice.")
    voice_path = input("  Voice sample file path (press Enter to skip): ").strip()

    voice_filename = None
    if voice_path:
        voice_filename = memory_bank.copy_voice_sample(patient_id, voice_path)
        if voice_filename:
            print(f"  Copied: {voice_filename}")
            # Attach voice sample to all new memories
            for m in new_memories:
                m["voice_sample_file"] = voice_filename

    # ── Save ─────────────────────────────────────────────────────────────────
    for m in new_memories:
        memory_bank.add_memory(patient_id, m)

    print()
    print(f"  Saved {len(new_memories)} memories for {profile['name']}.")
    if voice_filename:
        print(f"  Voice sample saved: {voice_filename}")
    print()
    print("  When a lucid moment happens, run:")
    print(f"    python main.py lucid_now --patient {patient_id}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MODE 2: LUCID NOW
# ─────────────────────────────────────────────────────────────────────────────

def run_lucid_now(patient_id: str) -> None:
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║       HEARTH — Lucid Moment Triggered    ║")
    print("  ╚══════════════════════════════════════════╝")
    print()

    # ── Load data ────────────────────────────────────────────────────────────
    try:
        profile = memory_bank.load_profile(patient_id)
    except FileNotFoundError as e:
        print(f"  Error: {e}")
        sys.exit(1)

    memories = memory_bank.load_memories(patient_id)
    if not memories:
        print("  Warning: No memories found. Run 'onboard' to add family memories first.")
        sys.exit(1)

    patient_name = profile["name"]
    print(f"  Patient: {patient_name}")
    print(f"  Memories loaded: {len(memories)}")
    print()
    print("  Generating artifacts... (this takes about 15-30 seconds)")
    print()

    # ── Output directory ─────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = ROOT / "data" / "outputs" / patient_id / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Agent ─────────────────────────────────────────────────────────────────
    agent = HearthAgent()

    photos_dir = memory_bank.get_photos_dir(patient_id)
    voice_samples_dir = memory_bank.get_voice_samples_dir(patient_id)
    photo_info = memory_bank.get_photo_context(patient_id, memories)

    results: dict[str, Path | None] = {}
    errors: dict[str, str] = {}

    # ── Generate all content via agent (can be parallelized) ─────────────────
    print("  [1/4] Generating letter content...")
    try:
        letter_text = agent.generate_letter(profile, memories)
    except Exception as e:
        letter_text = None
        errors["letter"] = str(e)
        print(f"    Error generating letter: {e}")

    print("  [2/4] Generating voice script...")
    try:
        voice_script = agent.generate_voice_script(profile, memories)
    except Exception as e:
        voice_script = None
        errors["voice"] = str(e)
        print(f"    Error generating voice script: {e}")

    print("  [3/4] Generating photo captions...")
    try:
        if photo_info:
            captions = agent.generate_photo_captions(profile, memories, photo_info)
        else:
            captions = None
            print("    No photos found — skipping photo story.")
    except Exception as e:
        captions = None
        errors["photo_story"] = str(e)
        print(f"    Error generating photo captions: {e}")

    print("  [4/4] Generating dialogue guide...")
    try:
        guide = agent.generate_dialogue_guide(profile, memories)
    except Exception as e:
        guide = None
        errors["dialogue_guide"] = str(e)
        print(f"    Error generating dialogue guide: {e}")

    print()
    print("  Rendering artifacts...")
    print()

    # ── Artifact 1: Letter PDF ────────────────────────────────────────────────
    if letter_text:
        try:
            from letter_generator import generate_letter_pdf
            letter_path = output_dir / f"letter_{patient_id}_{timestamp}.pdf"
            generate_letter_pdf(letter_text, profile, letter_path)
            results["letter"] = letter_path
            print(f"  [Letter PDF]       {letter_path.name}")
        except Exception as e:
            errors["letter_pdf"] = str(e)
            print(f"  [Letter PDF]       Error: {e}")
    else:
        print("  [Letter PDF]       Skipped (no content generated)")

    # ── Artifact 2: Voice message ─────────────────────────────────────────────
    if voice_script:
        try:
            from voice_generator import generate_voice_message
            voice_path = output_dir / f"voice_{patient_id}_{timestamp}.mp3"
            final_path, is_audio = generate_voice_message(
                voice_script, profile, voice_samples_dir, memories, voice_path
            )
            results["voice"] = final_path
            artifact_type = "Voice MP3" if is_audio else "Voice Script (text)"
            print(f"  [{artifact_type:<20}] {final_path.name}")
        except Exception as e:
            errors["voice_mp3"] = str(e)
            print(f"  [Voice]            Error: {e}")
    else:
        print("  [Voice]            Skipped (no script generated)")

    # ── Artifact 3: Photo story PDF ───────────────────────────────────────────
    if captions:
        try:
            from photo_story import generate_photo_story_pdf
            story_path = output_dir / f"photo_story_{patient_id}_{timestamp}.pdf"
            generate_photo_story_pdf(captions, profile, photos_dir, story_path)
            results["photo_story"] = story_path
            print(f"  [Photo Story PDF]  {story_path.name}")
        except Exception as e:
            errors["photo_story_pdf"] = str(e)
            print(f"  [Photo Story PDF]  Error: {e}")
    else:
        print("  [Photo Story PDF]  Skipped (no photos or captions)")

    # ── Artifact 4: Dialogue guide PDF ────────────────────────────────────────
    if guide:
        try:
            from dialogue_guide import generate_dialogue_guide_pdf
            guide_path = output_dir / f"dialogue_guide_{patient_id}_{timestamp}.pdf"
            generate_dialogue_guide_pdf(guide, profile, guide_path)
            results["dialogue_guide"] = guide_path
            print(f"  [Dialogue Guide]   {guide_path.name}")
        except Exception as e:
            errors["dialogue_guide_pdf"] = str(e)
            print(f"  [Dialogue Guide]   Error: {e}")
    else:
        print("  [Dialogue Guide]   Skipped (no guide generated)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("  ─" * 22)
    print(f"  Artifacts ready. Lucid moment package saved.")
    print(f"  Output folder: {output_dir}")
    print()

    if errors:
        print("  Issues encountered:")
        for k, v in errors.items():
            print(f"    {k}: {v}")
        print()

    artifact_count = len(results)
    print(f"  {artifact_count} artifact(s) generated successfully.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="hearth",
        description="Hearth — AI memory companion for Alzheimer's patients",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    onboard_parser = subparsers.add_parser(
        "onboard",
        help="Onboard a family member and collect memories for a patient",
    )
    onboard_parser.add_argument(
        "--patient",
        required=True,
        metavar="PATIENT_ID",
        help="Patient folder ID (e.g. margaret_chen)",
    )

    lucid_parser = subparsers.add_parser(
        "lucid_now",
        help="Trigger artifact generation during a lucid moment",
    )
    lucid_parser.add_argument(
        "--patient",
        required=True,
        metavar="PATIENT_ID",
        help="Patient folder ID (e.g. margaret_chen)",
    )

    args = parser.parse_args()

    if args.command == "onboard":
        run_onboard(args.patient)
    elif args.command == "lucid_now":
        run_lucid_now(args.patient)


if __name__ == "__main__":
    main()
