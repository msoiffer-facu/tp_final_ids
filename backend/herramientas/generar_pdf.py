from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


_COLOR_HEADER = colors.HexColor("#2C5282")
_COLOR_ROW_ALT = colors.HexColor("#EBF4FF")
_COLOR_ROW_EVEN = colors.white


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    width, _ = landscape(letter)
    canvas.drawString(2 * cm, 1 * cm, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    canvas.drawRightString(width - 2 * cm, 1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def generar_pdf_reporte(title, headers, rows, summary=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "cell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        wordWrap="CJK",
    )
    header_style = ParagraphStyle(
        "header_cell",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.white,
        fontName="Helvetica-Bold",
    )

    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 8))

    if summary:
        for label, value in summary:
            elements.append(Paragraph(f"<b>{label}:</b> {value}", styles["Normal"]))
        elements.append(Spacer(1, 8))

    # Convertir toda celda a Paragraph para que el texto wrappee correctamente
    header_row = [Paragraph(str(h), header_style) for h in headers]
    data_rows = [
        [Paragraph(str(cell) if cell is not None else "", cell_style) for cell in row]
        for row in rows
    ]
    data = [header_row] + data_rows

    # Ancho disponible
    page_width, _ = landscape(letter)
    available_width = page_width - 4 * cm
    col_width = available_width / max(len(headers), 1)
    col_widths = [col_width] * len(headers)

    table = Table(data, colWidths=col_widths, repeatRows=1)

    row_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), _COLOR_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_COLOR_ROW_EVEN, _COLOR_ROW_ALT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]

    table.setStyle(TableStyle(row_styles))
    elements.append(table)

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
