"""
dialogue_guide.py — Caregiver dialogue script PDF. Exact same parchment design as letter_generator.py.
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


def _draw_page_decoration(pdf: FPDF):
    """Exact copy of letter_generator._draw_page_decoration."""
    pdf.set_fill_color(252, 245, 228)
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_draw_color(180, 130, 60)
    pdf.set_line_width(1.8)
    pdf.rect(10, 10, 190, 277)
    pdf.set_draw_color(210, 170, 100)
    pdf.set_line_width(0.5)
    pdf.rect(13, 13, 184, 271)
    pdf.set_fill_color(180, 130, 60)
    for cx, cy in [(10, 10), (200, 10), (10, 287), (200, 287)]:
        pdf.ellipse(cx - 2.2, cy - 2.2, 4.4, 4.4, "F")


class HearthPDF(FPDF):
    """FPDF subclass that redraws parchment decoration on every page (including auto page breaks)."""
    def header(self):
        _draw_page_decoration(self)
        self.set_line_width(0.3)


def _divider(pdf: FPDF):
    """Exact divider from letter_generator."""
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(12)


def _closing_ornament(pdf: FPDF):
    """Exact closing ornament from letter_generator."""
    pdf.ln(10)
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(5)


def _section_heading(pdf: FPDF, text: str):
    """Section label — Times Bold 13, amber-brown, thin amber underline."""
    pdf.ln(6)
    pdf.set_font("Times", style="B", size=13)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 9, _safe(text), ln=True)
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.3)
    pdf.line(28, pdf.get_y(), 182, pdf.get_y())
    pdf.ln(6)


def _boxed_text(pdf: FPDF, text: str):
    """Quoted content block — parchment fill, amber border, Times 12."""
    pdf.set_fill_color(250, 243, 225)
    pdf.set_draw_color(180, 130, 60)
    pdf.set_line_width(0.5)
    pdf.set_font("Times", size=12)
    pdf.set_text_color(45, 30, 15)
    avail_w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(avail_w, 7, _safe(text), border=1, fill=True)
    pdf.set_x(pdf.l_margin)
    pdf.ln(3)


def generate_dialogue_guide_pdf(guide: dict, profile: dict, output_path: Path) -> Path:
    patient_name   = profile.get("name", "")
    patient_first  = patient_name.split()[0] if patient_name else patient_name
    family_contact = profile.get("primary_family_contact", "")
    family_display = family_contact.split("(")[0].strip() if family_contact else family_contact

    pdf = HearthPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(left=28, top=22, right=28)

    pdf.add_page()
    pdf.set_y(22)

    # ── Header ───────────────────────────────────────────────────────────────
    pdf.set_font("Times", style="B", size=24)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 12, _safe(f"Dialogue Guide for {patient_first}"), ln=True, align="C")
    pdf.ln(4)

    _divider(pdf)

    # ── 1. Opening ────────────────────────────────────────────────────────────
    _section_heading(pdf, "Opening")
    _boxed_text(pdf, guide.get("opening", ""))

    # ── 2. Memory Prompts ─────────────────────────────────────────────────────
    _section_heading(pdf, "Memory Prompts")

    w = pdf.w - pdf.l_margin - pdf.r_margin
    prompts = guide.get("memory_prompts", [])
    for i, prompt in enumerate(prompts, start=1):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Times", style="B", size=12)
        pdf.set_text_color(110, 70, 20)
        pdf.cell(w, 7, _safe(f"Prompt {i}"), ln=True)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Times", size=12)
        pdf.set_text_color(45, 30, 15)
        pdf.multi_cell(w, 7, _safe(f'"{prompt.get("prompt", "")}"'))

        why = prompt.get("why_it_works", "")
        if why:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="I", size=10)
            pdf.set_text_color(150, 115, 65)
            pdf.multi_cell(w, 6, _safe(why))

        followup = prompt.get("follow_up", "")
        if followup:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="I", size=10)
            pdf.set_text_color(155, 110, 55)
            pdf.multi_cell(w, 6, _safe(f'If she responds: "{followup}"'))

        pdf.ln(3)
        if i < len(prompts):
            pdf.set_draw_color(200, 155, 80)
            pdf.set_line_width(0.2)
            pdf.line(28, pdf.get_y(), 182, pdf.get_y())
            pdf.ln(4)

    # ── 3. Photo Sequence ─────────────────────────────────────────────────────
    photo_sequence = guide.get("photo_sequence", [])
    if photo_sequence:
        _section_heading(pdf, "Photo Sequence")
        pw = pdf.w - pdf.l_margin - pdf.r_margin
        for j, photo in enumerate(photo_sequence, start=1):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Times", style="B", size=12)
            pdf.set_text_color(110, 70, 20)
            pdf.cell(pw, 7, _safe(f"Photo {j}: {photo.get('photo', '')}"), ln=True)

            intro = photo.get("introduction", "")
            if intro:
                pdf.set_x(pdf.l_margin)
                pdf.set_font("Times", size=12)
                pdf.set_text_color(45, 30, 15)
                pdf.multi_cell(pw, 7, _safe(f'"{intro}"'))
            pdf.ln(3)

    # ── 4. If Distressed ──────────────────────────────────────────────────────
    _section_heading(pdf, "If Distressed")
    _boxed_text(pdf, guide.get("if_distressed", ""))

    # ── 5. Closing ────────────────────────────────────────────────────────────
    _section_heading(pdf, "Closing")
    _boxed_text(pdf, guide.get("closing", ""))

    # ── Quick reference ───────────────────────────────────────────────────────
    if profile.get("avoid_topics") or profile.get("calming_topics"):
        _section_heading(pdf, "Quick Reference")

        if profile.get("avoid_topics"):
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(155, 55, 45)
            pdf.cell(0, 7, "Avoid:", ln=True)
            pdf.set_font("Times", size=11)
            pdf.set_text_color(45, 30, 15)
            for topic in profile["avoid_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)
            pdf.ln(3)

        if profile.get("calming_topics"):
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(55, 110, 65)
            pdf.cell(0, 7, "Calming topics:", ln=True)
            pdf.set_font("Times", size=11)
            pdf.set_text_color(45, 30, 15)
            for topic in profile["calming_topics"]:
                pdf.cell(0, 6, _safe(f"  -  {topic}"), ln=True)

    _closing_ornament(pdf)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
