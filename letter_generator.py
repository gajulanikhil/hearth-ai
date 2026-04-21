"""
letter_generator.py — Generates a clean PDF letter using fpdf2.

Renders the Claude-generated letter text in a warm, readable typographic layout.
Font: Helvetica (built-in, no font files needed).
"""

from pathlib import Path
from fpdf import FPDF


# Mapping of common Unicode characters to Latin-1-safe equivalents.
# fpdf2's built-in Helvetica/Times/Courier fonts only cover Latin-1 (cp1252).
_UNICODE_MAP = str.maketrans({
    "\u2014": "--",   # em dash
    "\u2013": "-",    # en dash
    "\u2018": "'",    # left single quote
    "\u2019": "'",    # right single quote / apostrophe
    "\u201c": '"',    # left double quote
    "\u201d": '"',    # right double quote
    "\u2026": "...",  # ellipsis
    "\u2022": "-",    # bullet
    "\u00a0": " ",    # non-breaking space
})


def _safe(text: str) -> str:
    """Replace Unicode characters that Latin-1 cannot encode."""
    return text.translate(_UNICODE_MAP).encode("latin-1", errors="replace").decode("latin-1")


def generate_letter_pdf(letter_text: str, profile: dict, output_path: Path) -> Path:
    """
    Render the letter as a PDF and save to output_path.
    Returns the path to the created PDF.
    """
    patient_name = profile["name"]
    family_contact = profile["primary_family_contact"]

    pdf = FPDF()
    pdf.set_margins(left=25, top=25, right=25)
    pdf.add_page()

    # ── Header: subtle "Hearth" branding ────────────────────────────────────
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.set_text_color(180, 160, 140)
    pdf.cell(0, 8, _safe("Hearth -- a memory companion"), ln=True, align="R")
    pdf.ln(2)

    # ── Thin decorative rule ─────────────────────────────────────────────────
    pdf.set_draw_color(200, 180, 160)
    pdf.set_line_width(0.4)
    pdf.line(25, pdf.get_y(), 185, pdf.get_y())
    pdf.ln(10)

    # ── "A letter for" label ─────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="", size=10)
    pdf.set_text_color(140, 120, 100)
    pdf.cell(0, 7, _safe(f"A letter for {patient_name}"), ln=True, align="C")
    pdf.ln(2)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.cell(0, 6, _safe(f"From {family_contact}"), ln=True, align="C")
    pdf.ln(14)

    # ── Letter body ──────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", size=13)
    pdf.set_text_color(40, 30, 20)

    # Split into paragraphs to preserve intentional line breaks
    paragraphs = letter_text.strip().split("\n\n")
    for i, para in enumerate(paragraphs):
        para_text = _safe(para.replace("\n", " ").strip())
        if para_text:
            pdf.multi_cell(0, 8, para_text)
            if i < len(paragraphs) - 1:
                pdf.ln(5)

    # ── Bottom rule ──────────────────────────────────────────────────────────
    pdf.ln(12)
    pdf.set_draw_color(200, 180, 160)
    pdf.line(25, pdf.get_y(), 185, pdf.get_y())
    pdf.ln(6)

    # ── Footer ───────────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(180, 160, 140)
    pdf.cell(0, 5, "Generated with love by Hearth.", ln=True, align="C")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
