"""
memory_bank.py — Patient memory storage and retrieval.

Manages reading and writing profile.json and memories.json for each patient.
All data lives in data/patients/<patient_id>/.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent
PATIENTS_DIR = BASE_DIR / "data" / "patients"


def _patient_dir(patient_id: str) -> Path:
    return PATIENTS_DIR / patient_id


def _ensure_dirs(patient_id: str) -> None:
    d = _patient_dir(patient_id)
    (d / "photos").mkdir(parents=True, exist_ok=True)
    (d / "voice_samples").mkdir(parents=True, exist_ok=True)


def patient_exists(patient_id: str) -> bool:
    return (_patient_dir(patient_id) / "profile.json").exists()


def load_profile(patient_id: str) -> dict:
    path = _patient_dir(patient_id) / "profile.json"
    if not path.exists():
        raise FileNotFoundError(f"No profile found for patient '{patient_id}'. Run onboard first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(patient_id: str, profile: dict) -> None:
    _ensure_dirs(patient_id)
    path = _patient_dir(patient_id) / "profile.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def load_memories(patient_id: str) -> list:
    path = _patient_dir(patient_id) / "memories.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memories(patient_id: str, memories: list) -> None:
    _ensure_dirs(patient_id)
    path = _patient_dir(patient_id) / "memories.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)


def add_memory(patient_id: str, memory: dict) -> None:
    memories = load_memories(patient_id)
    memories.append(memory)
    save_memories(patient_id, memories)


def copy_photo(patient_id: str, src_path: str) -> Optional[str]:
    """Copy a photo into the patient's photos directory. Returns the filename."""
    src = Path(src_path)
    if not src.exists():
        print(f"  Warning: photo not found at {src_path}, skipping.")
        return None
    dest_dir = _patient_dir(patient_id) / "photos"
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    return src.name


def copy_voice_sample(patient_id: str, src_path: str) -> Optional[str]:
    """Copy a voice sample into the patient's voice_samples directory. Returns the filename."""
    src = Path(src_path)
    if not src.exists():
        print(f"  Warning: voice sample not found at {src_path}, skipping.")
        return None
    dest_dir = _patient_dir(patient_id) / "voice_samples"
    dest = dest_dir / src.name
    shutil.copy2(src, dest)
    return src.name


def get_photos_dir(patient_id: str) -> Path:
    return _patient_dir(patient_id) / "photos"


def get_voice_samples_dir(patient_id: str) -> Path:
    return _patient_dir(patient_id) / "voice_samples"


def list_photos(patient_id: str) -> list:
    """Return list of photo filenames in the patient's photos directory."""
    d = get_photos_dir(patient_id)
    if not d.exists():
        return []
    return [f.name for f in d.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}]


def get_photo_context(patient_id: str, memories: list) -> list:
    """
    Build a list of photo info dicts for agent consumption.
    Each dict: {filename, context (description from memories)}.
    """
    # Map photo filenames to memory context
    photo_map: dict[str, list[str]] = {}
    for m in memories:
        for photo in m.get("associated_photos", []):
            if photo not in photo_map:
                photo_map[photo] = []
            photo_map[photo].append(
                f"Memory from {m['submitted_by']} ({m['relationship']}): {m['memory_text'][:200]}"
            )

    actual_photos = list_photos(patient_id)
    result = []

    for filename in actual_photos:
        context_parts = photo_map.get(filename, [])
        result.append({
            "filename": filename,
            "context": " | ".join(context_parts) if context_parts else "family photo",
        })

    # Also add photos mentioned in memories but not yet on disk (agent can still caption them)
    for filename, context_parts in photo_map.items():
        if filename not in actual_photos:
            result.append({
                "filename": filename,
                "context": " | ".join(context_parts),
                "missing_file": True,
            })

    return result
