"""
photo_story.py — Captioned photo story PDF with warm parchment design.
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


def _double_rule(pdf: FPDF, wide: bool = False) -> None:
    y = pdf.get_y()
    l, r = (28, 182) if not wide else (20, 190)
    pdf.set_draw_color(200, 155, 80)
    pdf.set_line_width(0.6)
    pdf.line(l, y, r, y)
    pdf.set_line_width(0.2)
    pdf.line(l + 6, y + 1.5, r - 6, y + 1.5)
    pdf.ln(4)


def _try_embed_image(pdf: FPDF, image_path: Path, x: float, y: float, max_w: float, max_h: float) -> Optional[float]:
    try:
        import io
        from PIL import Image
        with Image.open(image_path) as img:
            img.load()
            orig_w, orig_h = img.size
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            ratio = min(max_w / orig_w, max_h / orig_h)
            display_w = orig_w * ratio
            display_h = orig_h * ratio
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=90)
            buf.seek(0)
        pdf.image(buf, x=x, y=y, w=display_w, h=display_h)
        return display_h
    except Exception:
        return None


def generate_photo_story_pdf(
    captions: list,
    profile: dict,
    photos_dir: Path,
    output_path: Path,
) -> Path:
    patient_name  = profile["name"]
    patient_first = patient_name.split()[0]

    pdf = HearthPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_margins(left=28, top=22, right=28)

    # ── Cover page ───────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_y(26)

    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")
    pdf.ln(2)

    _double_rule(pdf)
    pdf.ln(4)

    pdf.set_font("Times", style="B", size=26)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 13, _safe(f"{patient_first}'s Photo Story"), ln=True, align="C")

    pdf.ln(2)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(155, 110, 55)
    pdf.cell(0, 8, "Memories shared by family, with love.", ln=True, align="C")
    pdf.ln(4)

    _double_rule(pdf)
    pdf.ln(10)

    pdf.set_font("Times", style="I", size=11)
    pdf.set_text_color(140, 105, 60)
    pdf.multi_cell(
        0, 7,
        _safe(
            "A caregiver's guide: Show each photo gently. "
            "Read the caption aloud. Pause. Let the memory land. There is no rush."
        ),
        align="C",
    )

    pdf.ln(14)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")

    # ── One page per photo ───────────────────────────────────────────────────
    for item in captions:
        filename = item.get("filename", "")
        caption  = item.get("caption", "")

        pdf.add_page()

        # Small filename label top-right
        pdf.set_y(24)
        pdf.set_font("Times", style="I", size=9)
        pdf.set_text_color(170, 135, 80)
        pdf.cell(0, 5, _safe(filename), ln=True, align="R")
        pdf.ln(4)

        # Photo or placeholder
        img_path = photos_dir / filename
        img_used = False

        if img_path.exists():
            used_h = _try_embed_image(
                pdf, img_path,
                x=28, y=pdf.get_y(),
                max_w=154, max_h=120,
            )
            if used_h is not None:
                pdf.set_y(pdf.get_y() + used_h + 6)
                img_used = True

        if not img_used:
            box_y = pdf.get_y()
            pdf.set_draw_color(210, 170, 100)
            pdf.set_fill_color(250, 243, 225)
            pdf.rect(28, box_y, 154, 80, style="FD")
            pdf.set_y(box_y + 30)
            pdf.set_font("Times", style="I", size=11)
            pdf.set_text_color(160, 125, 70)
            pdf.cell(0, 8, _safe(f"[ {filename} ]"), ln=True, align="C")
            pdf.set_font("Times", style="I", size=9)
            pdf.cell(0, 6, "Place photo here", ln=True, align="C")
            pdf.set_y(box_y + 86)

        # Thin amber rule
        pdf.set_draw_color(200, 155, 80)
        pdf.set_line_width(0.4)
        pdf.line(28, pdf.get_y(), 182, pdf.get_y())
        pdf.ln(8)

        # Caption — Times 18pt (accessibility)
        pdf.set_font("Times", size=18)
        pdf.set_text_color(45, 30, 15)
        pdf.multi_cell(0, 10, _safe(caption))

        # Closing ornament if room
        if pdf.get_y() < 255:
            pdf.ln(6)
            pdf.set_font("Times", style="I", size=12)
            pdf.set_text_color(180, 130, 60)
            pdf.cell(0, 6, _safe("~ ~ ~"), ln=True, align="C")

    # ── Back page ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_y(110)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")
    pdf.ln(6)
    _double_rule(pdf)
    pdf.ln(6)
    pdf.set_font("Times", style="I", size=16)
    pdf.set_text_color(110, 70, 20)
    pdf.cell(0, 10, "Every photo holds a world.", ln=True, align="C")
    pdf.ln(6)
    _double_rule(pdf)
    pdf.ln(6)
    pdf.set_font("Times", style="I", size=13)
    pdf.set_text_color(180, 130, 60)
    pdf.cell(0, 8, _safe("~ ~ ~"), ln=True, align="C")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path
