"""
dialogue_guide.py — Caregiver dialogue script PDF with warm parchment design.
"""

from pathlib import Path

from fpdf import FPDF

_UNICODE_MAP = str.maketrans({
    "—": "--",
    "–": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    "•": "-",
    " ": " ",
})

def _safe(text: str) -> str:
    return text.translate(_UNICODE_MAP).encode("latin-1", errors="replace").decode("latin-1")


class HearthPDF(FPDF):
    def header(self):
        self.set_fill_color(252, 245, 228)
        self.rect(0, 0, 210, 297, "F")
        self.set_draw_color(180, 130, 60)
        self.set_line_width(1.8)
        self.rect(10, 10, 190, 277)
        self.set_draw_color(210, 170, 100)
        self.set_line_width(0.5)
        self.rect(13, 13, 184, 271)
        self.set_fill_color(180, 130, 60)
        for cx, cy in [(10, 10), (200, 10), (10, 287), (200, 287)]:
            self.ellipse(cx - 2.2, cy - 2.2, 4.4, 4.4, "F")
        self.set_line_width(0.3)


COLORS = {
    "heading":        (110, 70,  20),
    "label":          (155, 110, 55),
    "body":           (45,  30,  15),
    "muted":          (150, 115, 65),
    "rule":           (200, 155, 80),
    "accent_fill":    (250, 243, 225),
    "accent_border":  (180, 130, 60),
    "distress_fill":  (252, 240, 218),
    "distress_border":(180, 130, 60),
    "avoid":          (155, 55,  45),
    "calm":           (55,  110, 65),
}


def _double_rule(pdf: FPDF) -> None:
    y = pdf.get_y()
    pdf.set_draw_color(*COLORS["rule"])
    pdf.set_line_width(0.6)
    pdf.line(28, y, 182, y)
    pdf.set_line_width(0.2)
    pdf.line(34, y + 1.5, 176, y + 1.5)
    pdf.ln(5)


def _thin_rule(pdf: FPDF) -> None:
    pdf.set_draw_color(*COLORS["rule"])
    pdf.set_line_width(0.3)
    pdf.line(28, pdf.get_y(), 182, pdf.get_y())
    pdf.ln(5)


def _section_heading(pdf: FPDF, text: str) -> None:
    pdf.ln(5)
    pdf.set_font("Times", style="B", size=14)
    pdf.set_text_color(*COLORS["heading"])
    pdf.cell(0, 9, _safe(text), ln=True)
    _thin_rule(pdf)


def _boxed_text(pdf: FPDF, text: str, fill: tuple, border: tuple, font_size: int = 12) -> None:
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*border)
    pdf.set_line_width(0.5)
    pdf.set_font("Times", size=font_size)
    avail_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(avail_w, 7, _safe(text), border=1, fill=True)
    pdf.set_x(pdf.l_margin)
    pdf.ln(3)


def generate_dialogue_guide_pdf(guide: dict, profile: dict, output_path: Path) -> Path:
    patient_name   = profile["name"]
    patient_first  = patient_name.split()[0]
    family_contact = profile.get("primary_family_contact", "")
    family_display = family_contact.split("(")[0].strip() if family_contact else family_contact

    pdf = HearthPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(left=28, top=22, right=28)

    # ── Cover page ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_y(26)

    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(*COLORS["rule"])
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")
    pdf.ln(2)

    _double_rule(pdf)
    pdf.ln(4)

    pdf.set_font("Times", style="B", size=24)
    pdf.set_text_color(*COLORS["heading"])
    pdf.cell(0, 12, "Caregiver Dialogue Guide", ln=True, align="C")

    pdf.ln(2)
    pdf.set_font("Times", size=14)
    pdf.set_text_color(*COLORS["label"])
    pdf.cell(0, 8, _safe(f"For a visit with {patient_name}"), ln=True, align="C")

    pdf.ln(1)
    pdf.set_font("Times", style="I", size=12)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 7, _safe(f"Memories shared by {family_display}"), ln=True, align="C")
    pdf.ln(4)

    _double_rule(pdf)
    pdf.ln(8)

    pdf.set_font("Times", style="I", size=11)
    pdf.set_text_color(*COLORS["muted"])
    pdf.multi_cell(
        0, 7,
        _safe(
            "This guide is yours to hold. Read it before you go in. "
            "You don't need to follow it exactly -- use it as a map, not a script. "
            f"The goal is for {patient_first} to feel at home in her memories."
        ),
        align="C",
    )

    pdf.ln(12)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(*COLORS["rule"])
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")

    # ── 1. Opening ───────────────────────────────────────────────────────────
    _section_heading(pdf, "1.  Opening -- How to Greet Her")

    pdf.set_font("Times", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, "Read aloud, slowly. Make eye contact. No rush.", ln=True)
    pdf.ln(3)

    _boxed_text(pdf, guide.get("opening", ""), COLORS["accent_fill"], COLORS["accent_border"], 12)

    # ── 2. Memory Prompts ────────────────────────────────────────────────────
    _section_heading(pdf, "2.  Memory Prompts -- Five Things to Ask")

    pdf.set_font("Times", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(
        0, 6,
        _safe("Use these when there is a natural pause. One good prompt is enough."),
        ln=True,
    )
    pdf.ln(3)

    w = pdf.w - pdf.l_margin - pdf.r_margin
    prompts = guide.get("memory_prompts", [])
    for i, prompt in enumerate(prompts, start=1):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Times", style="B", size=12)
        pdf.set_text_color(*COLORS["label"])
        pdf.cell(w, 7, f"Prompt {i}:", ln=True)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Times", size=12)
        pdf.set_text_color(*COLORS["body"])
        pdf.multi_cell(w, 7, _safe(f"\"{prompt.get('prompt', '')}\""))

        why = prompt.get("why_it_works", "")
        if why:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="I", size=10)
            pdf.set_text_color(*COLORS["muted"])
            pdf.multi_cell(w, 6, _safe(f"Why: {why}"))

        followup = prompt.get("follow_up", "")
        if followup:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="I", size=10)
            pdf.set_text_color(*COLORS["label"])
            pdf.multi_cell(w, 6, _safe(f"If she responds: \"{followup}\""))

        pdf.ln(3)
        if i < len(prompts):
            _thin_rule(pdf)

    # ── 3. Photo Sequence ────────────────────────────────────────────────────
    _section_heading(pdf, "3.  Photo Sequence -- What to Show and When")

    photo_sequence = guide.get("photo_sequence", [])
    if photo_sequence:
        pdf.set_font("Times", style="I", size=10)
        pdf.set_text_color(*COLORS["muted"])
        pdf.cell(0, 6, "Show photos one at a time. Let her look before you speak.", ln=True)
        pdf.ln(3)

        pw = pdf.w - pdf.l_margin - pdf.r_margin
        for j, photo in enumerate(photo_sequence, start=1):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(*COLORS["label"])
            pdf.cell(pw, 7, _safe(f"Photo {j}: {photo.get('photo', '')}"), ln=True)

            intro = photo.get("introduction", "")
            if intro:
                pdf.set_x(pdf.l_margin)
                pdf.set_font("Times", size=11)
                pdf.set_text_color(*COLORS["body"])
                pdf.multi_cell(pw, 7, _safe(f"\"{intro}\""))
            pdf.ln(3)
    else:
        pdf.set_font("Times", style="I", size=11)
        pdf.set_text_color(*COLORS["muted"])
        pdf.cell(0, 7, "See the Photo Story PDF for photos and captions.", ln=True)
        pdf.ln(3)

    # ── 4. If Distressed ─────────────────────────────────────────────────────
    _section_heading(pdf, "4.  If She Becomes Distressed")

    pdf.set_font("Times", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, _safe("Don't panic. Don't correct her. Ground her gently."), ln=True)
    pdf.ln(3)

    _boxed_text(
        pdf,
        guide.get("if_distressed", ""),
        COLORS["distress_fill"],
        COLORS["distress_border"],
        12,
    )

    # ── 5. Closing ────────────────────────────────────────────────────────────
    _section_heading(pdf, "5.  Closing -- How to End the Visit")

    pdf.set_font("Times", style="I", size=10)
    pdf.set_text_color(*COLORS["muted"])
    pdf.cell(0, 6, _safe("Leave her feeling safe. Say 'see you soon', not 'goodbye'."), ln=True)
    pdf.ln(3)

    _boxed_text(pdf, guide.get("closing", ""), COLORS["accent_fill"], COLORS["accent_border"], 12)

    # ── Quick reference (avoid / calming topics) ─────────────────────────────
    if profile.get("avoid_topics") or profile.get("calming_topics"):
        _section_heading(pdf, "Quick Reference")

        if profile.get("avoid_topics"):
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(*COLORS["avoid"])
            pdf.cell(0, 7, "AVOID these topics:", ln=True)
            pdf.set_font("Times", size=11)
            pdf.set_text_color(*COLORS["body"])
            for topic in profile["avoid_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)
            pdf.ln(3)

        if profile.get("calming_topics"):
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(*COLORS["calm"])
            pdf.cell(0, 7, "CALMING topics (redirect here if needed):", ln=True)
            pdf.set_font("Times", size=11)
            pdf.set_text_color(*COLORS["body"])
            for topic in profile["calming_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)

    # ── Closing ornament ─────────────────────────────────────────────────────
    pdf.ln(10)
    _double_rule(pdf)
    pdf.ln(4)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(*COLORS["rule"])
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
