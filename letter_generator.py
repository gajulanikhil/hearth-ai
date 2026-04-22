"""
letter_generator.py — Beautiful parchment-style PDF letter using fpdf2.
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
    """Warm parchment background + elegant double border + corner diamonds."""
    # Parchment background
    pdf.set_fill_color(252, 245, 228)
    pdf.rect(0, 0, 210, 297, "F")

    # Outer border — warm amber
    pdf.set_draw_color(180, 130, 60)
    pdf.set_line_width(1.8)
    pdf.rect(10, 10, 190, 277)

    # Inner border — lighter gold
    pdf.set_draw_color(210, 170, 100)
    pdf.set_line_width(0.5)
    pdf.rect(13, 13, 184, 271)

    # Corner diamonds (small filled squares rotated via two triangles)
    pdf.set_fill_color(180, 130, 60)
    for cx, cy in [(10, 10), (200, 10), (10, 287), (200, 287)]:
        pdf.set_fill_color(180, 130, 60)
        pdf.ellipse(cx - 2.2, cy - 2.2, 4.4, 4.4, "F")


def generate_letter_pdf(letter_text: str, profile: dict, output_path: Path) -> Path:
    patient_name  = profile.get("name", "")
    family_contact = profile.get("primary_family_contact", "")

    # Strip parenthetical relationship info if present, e.g. "David Chen (son)"
    family_display = family_contact.split("(")[0].strip() if family_contact else family_contact

    patient_first = patient_name.split()[0] if patient_name else patient_name

    pdf = FPDF()
    pdf.set_margins(left=28, top=20, right=28)
    pdf.add_page()

    _draw_page_decoration(pdf)

    pdf.set_y(22)

    # ── Decorative top ornament ──────────────────────────────────────────────
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")
    pdf.ln(2)

    # ── Title: A letter to {patient_first} ──────────────────────────────────
    pdf.set_font("Times", style="B", size=24)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 12, _safe(f"A Letter to {patient_first}"), ln=True, align="C")

    # ── Subtitle: from {family_member} ──────────────────────────────────────
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(155, 110, 55)
    pdf.cell(0, 8, _safe(f"from {family_display}"), ln=True, align="C")
    pdf.ln(4)

    # ── Divider rule ─────────────────────────────────────────────────────────
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(12)

    # ── Letter body ──────────────────────────────────────────────────────────
    pdf.set_font("Times", size=13)
    pdf.set_text_color(45, 30, 15)

    paragraphs = letter_text.strip().split("\n\n")
    for i, para in enumerate(paragraphs):
        para_text = _safe(para.replace("\n", " ").strip())
        if para_text:
            pdf.multi_cell(0, 8, para_text)
            if i < len(paragraphs) - 1:
                pdf.ln(5)

    # ── Closing ornament ─────────────────────────────────────────────────────
    pdf.ln(10)
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
