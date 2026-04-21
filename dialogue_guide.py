"""
dialogue_guide.py — Generates the caregiver dialogue script as a PDF.

Designed to be printed and held in hand. Large, scannable sections.
Includes opening, 5 memory prompts, photo sequence, distress protocol, closing.
"""

from pathlib import Path

from fpdf import FPDF

_UNICODE_MAP = str.maketrans({
    "\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"',  "\u201d": '"', "\u2026": "...", "\u2022": "-",
    "\u00a0": " ",
})

def _safe(text: str) -> str:
    return text.translate(_UNICODE_MAP).encode("latin-1", errors="replace").decode("latin-1")

# Section color palette (R, G, B)
COLORS = {
    "heading": (80, 50, 30),
    "label": (120, 85, 55),
    "body": (40, 30, 20),
    "muted": (150, 120, 95),
    "rule": (200, 175, 150),
    "accent_fill": (252, 247, 240),
    "accent_border": (215, 190, 165),
    "distress_fill": (255, 248, 240),
    "distress_border": (220, 180, 140),
}


def _rule(pdf: FPDF, light: bool = False) -> None:
    c = (220, 200, 180) if light else COLORS["rule"]
    pdf.set_draw_color(*c)
    pdf.set_line_width(0.3 if light else 0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)


def _section_heading(pdf: FPDF, text: str) -> None:
    pdf.ln(4)
    pdf.set_font("Helvetica", style="B", size=13)
    pdf.set_text_color(*COLORS["heading"])
    pdf.cell(0, 9, _safe(text.upper()), ln=True)
    _rule(pdf, light=True)


def _boxed_text(pdf: FPDF, text: str, fill: tuple, border: tuple, font_size: int = 12) -> None:
    """Render text in a lightly filled box."""
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.4)
    pdf.set_font("Helvetica", size=font_size)
    # Compute available width explicitly to avoid layout state issues
    avail_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(avail_w, 7, _safe(text), border=1, fill=True)
    pdf.set_x(pdf.l_margin)
    pdf.ln(2)


def generate_dialogue_guide_pdf(guide: dict, profile: dict, output_path: Path) -> Path:
    """
    Render the caregiver dialogue guide as a PDF.

    guide keys: opening, memory_prompts, photo_sequence, if_distressed, closing
    """
    patient_name = profile["name"]
    patient_first = patient_name.split()[0]
    family_contact = profile["primary_family_contact"]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 15, 15)

    # ── Cover ────────────────────────────────────────────────────────────────
    pdf.add_page()

    pdf.set_font("Helvetica", style="I", size=9)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, "Hearth -- a memory companion", ln=True, align="R")
    pdf.ln(20)

    pdf.set_font("Helvetica", style="B", size=26)
    pdf.set_text_color(*COLORS["heading"])
    pdf.cell(0, 13, "Caregiver Dialogue Guide", ln=True, align="C")

    pdf.ln(4)
    pdf.set_font("Helvetica", size=14)
    pdf.set_text_color(*COLORS["label"])
    pdf.cell(0, 9, _safe(f"For a visit with {patient_name}"), ln=True, align="C")

    pdf.ln(3)
    pdf.set_font("Helvetica", style="I", size=11)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 7, _safe(f"Family memories shared by {family_contact}"), ln=True, align="C")

    pdf.ln(12)
    _rule(pdf)
    pdf.ln(6)

    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.multi_cell(
        0,
        7,
        _safe(
            "This guide is yours to hold. Read it before you go in. "
            "You don't need to follow it exactly -- use it as a map, not a script. "
            f"The goal is for {patient_first} to feel at home in her memories."
        ),
        align="C",
    )

    # ── 1. Opening ───────────────────────────────────────────────────────────
    _section_heading(pdf, "1. Opening -- How to Greet Her")

    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, "Read aloud, slowly. Make eye contact. No rush.", ln=True)
    pdf.ln(3)

    _boxed_text(pdf, guide.get("opening", ""), COLORS["accent_fill"], COLORS["accent_border"], 12)

    # ── 2. Memory Prompts ────────────────────────────────────────────────────
    _section_heading(pdf, "2. Memory Prompts -- Five Things to Ask")

    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(
        0, 6,
        _safe("Use these when there's a natural pause. Don't rush through them -- one good one is enough."),
        ln=True
    )
    pdf.ln(3)

    w = pdf.w - pdf.l_margin - pdf.r_margin
    for i, prompt in enumerate(guide.get("memory_prompts", []), start=1):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(*COLORS["label"])
        pdf.cell(w, 7, f"Prompt {i}:", ln=True)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(*COLORS["body"])
        pdf.multi_cell(w, 7, _safe(f"\"{prompt.get('prompt', '')}\""))

        why = prompt.get("why_it_works", "")
        if why:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", style="I", size=10)
            pdf.set_text_color(*COLORS["muted"])
            pdf.multi_cell(w, 6, _safe(f"Why: {why}"))

        followup = prompt.get("follow_up", "")
        if followup:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", style="I", size=10)
            pdf.set_text_color(*COLORS["label"])
            pdf.multi_cell(w, 6, _safe(f"If she responds: \"{followup}\""))

        pdf.ln(4)
        if i < len(guide.get("memory_prompts", [])):
            _rule(pdf, light=True)

    # ── 3. Photo Sequence ────────────────────────────────────────────────────
    _section_heading(pdf, "3. Photo Sequence -- What to Show and When")

    photo_sequence = guide.get("photo_sequence", [])
    if photo_sequence:
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.set_text_color(*COLORS["muted"])
        pdf.cell(0, 6, "Show photos one at a time. Let her look before you speak.", ln=True)
        pdf.ln(3)

        pw = pdf.w - pdf.l_margin - pdf.r_margin
        for j, photo in enumerate(photo_sequence, start=1):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.set_text_color(*COLORS["label"])
            pdf.cell(pw, 7, _safe(f"Photo {j}: {photo.get('photo', '')}"), ln=True)

            intro = photo.get("introduction", "")
            if intro:
                pdf.set_x(pdf.l_margin)
                pdf.set_font("Helvetica", size=11)
                pdf.set_text_color(*COLORS["body"])
                pdf.multi_cell(pw, 7, _safe(f"\"{intro}\""))

            pdf.ln(3)
    else:
        pdf.set_font("Helvetica", style="I", size=11)
        pdf.set_text_color(*COLORS["muted"])
        pdf.cell(0, 7, "See the Photo Story PDF for photos and captions.", ln=True)
        pdf.ln(3)

    # ── 4. If Distressed ─────────────────────────────────────────────────────
    _section_heading(pdf, "4. If She Becomes Distressed")

    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, _safe("Don't panic. Don't correct her. Ground her gently."), ln=True)
    pdf.ln(3)

    _boxed_text(
        pdf,
        guide.get("if_distressed", ""),
        COLORS["distress_fill"],
        COLORS["distress_border"],
        12
    )

    # ── 5. Closing ────────────────────────────────────────────────────────────
    _section_heading(pdf, "5. Closing -- How to End the Visit")

    pdf.set_font("Helvetica", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, _safe("Leave her feeling safe. Don't say 'goodbye' -- say 'see you soon'."), ln=True)
    pdf.ln(3)

    _boxed_text(pdf, guide.get("closing", ""), COLORS["accent_fill"], COLORS["accent_border"], 12)

    # ── Quick reference card (avoids / calms) ───────────────────────────────
    if profile.get("avoid_topics") or profile.get("calming_topics"):
        pdf.ln(4)
        _section_heading(pdf, "Quick Reference")

        if profile.get("avoid_topics"):
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.set_text_color(160, 60, 50)
            pdf.cell(0, 7, "AVOID these topics:", ln=True)
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(*COLORS["body"])
            for topic in profile["avoid_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)
            pdf.ln(3)

        if profile.get("calming_topics"):
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.set_text_color(60, 120, 70)
            pdf.cell(0, 7, "CALMING topics (redirect here if needed):", ln=True)
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(*COLORS["body"])
            for topic in profile["calming_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)

    # ── Footer ───────────────────────────────────────────────────────────────
    pdf.ln(10)
    _rule(pdf)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 5, "Generated with love by Hearth. You are doing something beautiful.", ln=True, align="C")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
