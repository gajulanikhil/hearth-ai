"""
photo_story.py — Captioned photo story PDF. Exact same parchment design as letter_generator.py.
"""

from pathlib import Path
from typing import Optional

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


def _divider(pdf: FPDF):
    """Exact divider from letter_generator (thick then thin, coordinates 38-172 / 44-166)."""
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(12)


def _closing_ornament(pdf: FPDF):
    """Exact closing ornament from letter_generator (thin then thick, then ~ ~ ~)."""
    pdf.ln(10)
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.2)
    pdf.line(44, pdf.get_y(), 166, pdf.get_y())
    pdf.ln(1)
    pdf.set_line_width(0.6)
    pdf.line(38, pdf.get_y(), 172, pdf.get_y())
    pdf.ln(5)


def _try_embed_image(
    pdf: FPDF, image_path: Path,
    x: float, y: float, max_w: float, max_h: float,
) -> Optional[float]:
    try:
        import io
        from PIL import Image
        with Image.open(image_path) as img:
            img.load()
            orig_w, orig_h = img.size
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            ratio = min(max_w / orig_w, max_h / orig_h)
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=90)
            buf.seek(0)
        pdf.image(buf, x=x, y=y, w=orig_w * ratio, h=orig_h * ratio)
        return orig_h * ratio
    except Exception:
        return None


def generate_photo_story_pdf(
    captions: list,
    profile: dict,
    photos_dir: Path,
    output_path: Path,
) -> Path:
    patient_name   = profile.get("name", "")
    patient_first  = patient_name.split()[0] if patient_name else patient_name
    family_contact = profile.get("primary_family_contact", "")
    family_display = family_contact.split("(")[0].strip() if family_contact else family_contact

    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(left=28, top=20, right=28)

    # ── Cover page — mirrors letter header exactly ────────────────────────────
    pdf.add_page()
    _draw_page_decoration(pdf)
    pdf.set_y(22)

    pdf.set_font("Times", style="B", size=24)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 12, _safe(f"{patient_first}'s Photo Story"), ln=True, align="C")
    pdf.ln(4)

    _divider(pdf)

    # ── One page per photo ────────────────────────────────────────────────────
    for item in captions:
        filename = item.get("filename", "")
        caption  = item.get("caption", "")

        pdf.add_page()
        _draw_page_decoration(pdf)
        pdf.set_y(22)

        # Embed photo or draw placeholder
        img_path = photos_dir / filename
        img_used = False

        if img_path.exists():
            used_h = _try_embed_image(pdf, img_path, x=28, y=pdf.get_y(), max_w=154, max_h=130)
            if used_h is not None:
                pdf.set_y(pdf.get_y() + used_h + 6)
                img_used = True

        if not img_used:
            box_y = pdf.get_y()
            pdf.set_draw_color(210, 170, 100)
            pdf.set_fill_color(250, 243, 225)
            pdf.rect(28, box_y, 154, 90, style="FD")
            pdf.set_y(box_y + 36)
            pdf.set_font("Times", style="I", size=11)
            pdf.set_text_color(160, 125, 70)
            pdf.cell(0, 8, _safe(f"[ {filename} ]"), ln=True, align="C")
            pdf.set_y(box_y + 96)

        # Thin amber rule — matches the letter's draw color
        pdf.set_draw_color(200, 155, 80)
        pdf.set_line_width(0.4)
        pdf.line(38, pdf.get_y(), 172, pdf.get_y())
        pdf.ln(8)

        # Caption — Times 13 body style (18pt minimum for accessibility)
        pdf.set_font("Times", size=18)
        pdf.set_text_color(45, 30, 15)
        pdf.multi_cell(0, 10, _safe(caption))

        # Closing ornament if room above border
        if pdf.get_y() < 248:
            _closing_ornament(pdf)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
