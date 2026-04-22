"""
agent.py — OpenAI-powered artifact generation engine.

Uses the OpenAI SDK to make targeted calls for each artifact.
"""

import json
import os

from openai import OpenAI, AuthenticationError
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    "You are Hearth, a compassionate AI designed to help Alzheimer's patients feel "
    "connected to their families during lucid moments. You have deep knowledge of "
    "dementia care best practices. You generate artifacts that are warm, specific, "
    "simple, and grounded in real shared memories. You never use medical language. "
    "You never reference the disease. You speak only in warmth and memory. Every word "
    "you generate should make the patient feel loved and safe."
)

MODEL = "gpt-4o"


def _clean_json(text: str) -> str:
    """Strip markdown code fences from a JSON response."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _build_patient_context(profile: dict, memories: list) -> str:
    memories_text = "\n\n".join(
        f"Memory from {m['submitted_by']} ({m['relationship']}):\n"
        f"{m['memory_text']}\n"
        f"Emotional tone: {m.get('emotional_tone', 'warm')}\n"
        f"Associated photos: {', '.join(m.get('associated_photos', [])) or 'none'}"
        for m in memories
    )

    return (
        f"PATIENT PROFILE:\n"
        f"Name: {profile['name']}\n"
        f"Age: {profile['age']}\n"
        f"Primary family contact: {profile['primary_family_contact']}\n"
        f"Emotional anchors: {', '.join(profile.get('emotional_anchors', []))}\n"
        f"Calming topics: {', '.join(profile.get('calming_topics', []))}\n"
        f"Topics to avoid: {', '.join(profile.get('avoid_topics', []))}\n"
        f"Current mood baseline: {profile.get('current_mood_baseline', '')}\n"
        f"Best time of day: {profile.get('best_time_of_day', '')}\n\n"
        f"FAMILY MEMORIES:\n{memories_text}"
    )


class HearthAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY") or None
        try:
            self.client = OpenAI(api_key=api_key)
        except AuthenticationError:
            raise EnvironmentError(
                "OPENAI_API_KEY not found or invalid. Add it to your .env file:\n"
                "  OPENAI_API_KEY=sk-..."
            )

    def _call(self, context: str, user_instruction: str, max_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{context}\n\n{user_instruction}"},
            ],
        )
        return response.choices[0].message.content

    def generate_letter(self, profile: dict, memories: list) -> str:
        context = _build_patient_context(profile, memories)
        family_member = profile["primary_family_contact"]
        patient_first = profile["name"].split()[0]

        instruction = (
            f"Write a letter FROM {family_member} TO {patient_first}.\n\n"
            "Rules:\n"
            f"- Write in first person AS {family_member}\n"
            "- Use specific memories they shared — real names, real places, real details\n"
            "- Sound like a real person who loves this patient deeply\n"
            "- Approximately 200 words\n"
            "- Warm, simple language — written, not spoken\n"
            "- No mention of disease, care home, or medical context whatsoever\n"
            "- No salutation header needed; no sign-off line needed\n"
            f"- Address {patient_first} by first name naturally within the text\n"
            "- Just write love and shared memory.\n\n"
            "Write only the letter body text."
        )
        return self._call(context, instruction, max_tokens=800)

    def generate_voice_script(self, profile: dict, memories: list) -> str:
        context = _build_patient_context(profile, memories)
        family_member = profile["primary_family_contact"]
        patient_first = profile["name"].split()[0]

        instruction = (
            f"Write a SHORT voice message (60-80 words exactly) FROM {family_member} TO {patient_first}.\n\n"
            "Rules:\n"
            "- Natural spoken language — this will be recorded as audio\n"
            f"- First person as {family_member}\n"
            "- Reference 1-2 specific concrete memories with real details\n"
            "- Intimate and warm, like leaving a phone message for someone you love\n"
            "- No disease or care home references\n"
            f"- Begin with '{patient_first},' and end with a warm closing\n"
            "- EXACTLY 60-80 words\n\n"
            "Write only the script text, nothing else."
        )
        return self._call(context, instruction, max_tokens=300)

    def generate_photo_captions(self, profile: dict, memories: list, photo_info: list) -> list:
        context = _build_patient_context(profile, memories)
        patient_first = profile["name"].split()[0]

        photos_text = "\n".join(
            f"- {p['filename']}: {p.get('context', 'family photo')}"
            for p in photo_info
        )

        instruction = (
            f"Generate warm, spoken captions for these family photos to be read aloud to {patient_first} by a caregiver.\n\n"
            f"Photos:\n{photos_text}\n\n"
            "For each photo write 2-3 sentences that:\n"
            f"- Use second person ('you', 'your') addressing {patient_first} directly\n"
            "- Reference specific sensory and emotional details from the associated memory\n"
            "- Are simple and natural enough to read aloud in a calm room\n"
            "- Sound like storytelling, not clinical description\n\n"
            "Return ONLY a JSON array in this exact format:\n"
            '[{"filename": "photo.jpg", "caption": "The 2-3 sentence caption."}]\n\n'
            "No markdown, no extra text — only the JSON array."
        )

        raw = self._call(context, instruction, max_tokens=1200)
        return json.loads(_clean_json(raw))

    def generate_dialogue_guide(self, profile: dict, memories: list) -> dict:
        context = _build_patient_context(profile, memories)
        patient_first = profile["name"].split()[0]
        family_member = profile["primary_family_contact"]

        all_photos = []
        for m in memories:
            all_photos.extend(m.get("associated_photos", []))
        photos_str = ", ".join(all_photos) if all_photos else "the photo story PDF"

        instruction = (
            f"Generate a structured caregiver dialogue guide for a visit with {patient_first}.\n\n"
            f"Available photos/materials: {photos_str}\n"
            f"Family member who submitted memories: {family_member}\n\n"
            "Return ONLY a JSON object in this exact format (no markdown):\n"
            "{\n"
            f'  "opening": "2-3 sentence script to gently greet and orient {patient_first}. Warm, unhurried. Use her first name.",\n'
            '  "memory_prompts": [\n'
            '    {"prompt": "Question to ask", "why_it_works": "Brief caregiver note", "follow_up": "Natural follow-up if she responds positively"}\n'
            "    // 5 prompts total\n"
            "  ],\n"
            '  "photo_sequence": [\n'
            '    {"photo": "filename or description", "introduction": "What the caregiver says when showing this"}\n'
            "  ],\n"
            f'  "if_distressed": "3-4 sentence script for what to do and say if {patient_first} becomes anxious or upset. Grounding, gentle, redirect to a calming topic.",\n'
            f'  "closing": "2-3 sentence script to end the interaction gently, leaving {patient_first} feeling safe and loved."\n'
            "}\n\n"
            "No markdown — only the JSON object."
        )

        raw = self._call(context, instruction, max_tokens=2000)
        return json.loads(_clean_json(raw))
