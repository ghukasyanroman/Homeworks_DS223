"""Render the written report_source.md file to PDF."""

from pathlib import Path
import html
import re

import reportlab
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

ROOT = Path(__file__).resolve().parent

def inline(text):
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#087f8c">\1</link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="BodyFont" size="8.1">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r'<b>\1</b>', text)
    return text

def create_pdf(source):
    font_directory = Path(reportlab.__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont("BodyFont", str(font_directory / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("BodyFontBold", str(font_directory / "VeraBd.ttf")))
    pdfmetrics.registerFontFamily("BodyFont", normal="BodyFont", bold="BodyFontBold",
                                 italic="BodyFont", boldItalic="BodyFontBold")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyTextCustom", fontName="BodyFont", fontSize=8.9, leading=12.5,
                              spaceAfter=8, textColor=colors.HexColor("#253246")))
    styles.add(ParagraphStyle(name="TitleCustom", fontName="BodyFontBold", fontSize=21, leading=26,
                              textColor=colors.HexColor("#153248"), spaceAfter=13))
    styles.add(ParagraphStyle(name="H2Custom", fontName="BodyFontBold", fontSize=14, leading=18,
                              textColor=colors.HexColor("#153248"), spaceBefore=3, spaceAfter=11))
    styles.add(ParagraphStyle(name="H3Custom", fontName="BodyFontBold", fontSize=10, leading=13,
                              textColor=colors.HexColor("#087f8c"), spaceBefore=8, spaceAfter=6))
    styles.add(ParagraphStyle(name="CellCustom", fontName="BodyFont", fontSize=7.8, leading=10.4,
                              textColor=colors.HexColor("#253246")))
    styles.add(ParagraphStyle(name="HeaderCellCustom", parent=styles["CellCustom"], fontName="BodyFontBold",
                              textColor=colors.white))
    styles.add(ParagraphStyle(name="CaptionCustom", fontName="BodyFont", fontSize=7.1, leading=9.5,
                              textColor=colors.HexColor("#697585"), spaceAfter=7))
    width = 499.3
    story = []
    for block in source.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif block.startswith("!["):
            match = re.match(r"!\[([^\]]+)\]\(([^)]+)\)", block)
            path = (ROOT / "report" / match.group(2)).resolve()
            iw, ih = ImageReader(str(path)).getSize()
            story.append(Image(str(path), width=width, height=width * ih / iw))
            caption = ("Source: EIA observations [R3] and my fitted model." if "microwave_fit" in path.name
                       else "Source: my calculations using EIA-based rates, Census households and Fermi assumptions.")
            story.append(Paragraph(inline(match.group(1)) + ". " + caption, styles["CaptionCustom"]))
        elif block.startswith("|"):
            rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in block.splitlines()]
            rows.pop(1)
            weights = [max(len(row[col]) for row in rows) for col in range(len(rows[0]))]
            # Keep enough width for wrapped column labels and align numerical tables.
            weights = [max(11, min(value, 30)) for value in weights]
            col_widths = [width * value / sum(weights) for value in weights]
            cells = [[Paragraph(inline(cell), styles["HeaderCellCustom" if ri == 0 else "CellCustom"])
                      for cell in row] for ri, row in enumerate(rows)]
            table = Table(cells, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#153248")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f5f7")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#153248")),
            ]))
            story += [table, Spacer(1, 8)]
        else:
            style = "BodyTextCustom"
            if block.startswith("### "):
                style, block = "H3Custom", block[4:]
            elif block.startswith("## "):
                style, block = "H2Custom", block[3:]
            elif block.startswith("# "):
                style, block = "TitleCustom", block[2:]
            story.append(Paragraph(inline(block.replace("\n", " ")), styles[style]))

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#d7e1e5"))
        canvas.line(48, 36, 547, 36)
        canvas.setFillColor(colors.HexColor("#697585"))
        canvas.setFont("BodyFont", 7.1)
        canvas.drawString(48, 24, "Roman Ghukasyan | Posha diffusion analysis")
        canvas.drawRightString(547, 24, str(doc.page))

    doc = SimpleDocTemplate(str(ROOT / "report/report.pdf"), pagesize=(595.28, 841.89),
                            leftMargin=48, rightMargin=48, topMargin=40, bottomMargin=48,
                            title="Bass Model Analysis of Posha in the United States",
                            author="Roman Ghukasyan")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def build_report():
    """Create the PDF from the written report and the notebook's charts."""
    source_path = ROOT / "report/report_source.md"
    source = source_path.read_text(encoding="utf-8")
    create_pdf(source)
    return ROOT / "report/report.pdf"
