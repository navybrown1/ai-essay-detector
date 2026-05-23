import io
import datetime
from .preprocessor import segment_paragraphs, segment_sentences


def generate_pdf_report(
    text: str,
    ai_score: float,
    human_score: float,
    mixed_score: float,
    confidence: str,
    category_breakdown: dict,
    highlighted_sections: list,
    summary: str,
) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable,
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontSize=22, spaceAfter=6, textColor=colors.HexColor("#1a1a2e")
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=10, textColor=colors.gray, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "SectionHead", parent=styles["Heading2"],
        fontSize=14, spaceAfter=8, spaceBefore=16,
        textColor=colors.HexColor("#16213e")
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, leading=14, spaceAfter=6
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"],
        fontSize=8, textColor=colors.gray, italic=True, spaceAfter=12
    )

    story = []
    story.append(Paragraph("AI Writing Detection Report", title_style))
    story.append(
        Paragraph(
            f"Generated: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}",
            subtitle_style
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Disclaimer", section_style))
    story.append(Paragraph(
        "AI writing detection is probabilistic, not conclusive. "
        "The scores below indicate how closely the text's linguistic patterns "
        "match those commonly observed in AI-generated writing, but they do not "
        "prove authorship. False positives are possible, especially with "
        "well-structured formal writing, non-native English, or writing in "
        "certain academic genres. This report should never be used as the sole "
        "basis for academic or disciplinary decisions.",
        disclaimer_style
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Overall Scores", section_style))

    score_data = [
        ["Category", "Score", "Interpretation"],
        ["AI-Likelihood", f"{ai_score:.0%}",
         "High" if ai_score > 0.6 else "Moderate" if ai_score > 0.35 else "Low"],
        ["Human-Likelihood", f"{human_score:.0%}",
         "High" if human_score > 0.6 else "Moderate" if human_score > 0.35 else "Low"],
        ["Mixed Writing", f"{mixed_score:.0%}",
         "High" if mixed_score > 0.3 else "Moderate" if mixed_score > 0.15 else "Low"],
        ["Confidence", confidence,
         "Overall reliability of this assessment"],
    ]
    score_table = Table(score_data, colWidths=[1.5*inch, 1*inch, 2.5*inch])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f0f0f5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Summary", section_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Category Breakdown", section_style))

    cat_data = [["Category", "AI Pattern Score", "Weight"]]
    for cat, details in sorted(category_breakdown.items()):
        score_val = details.get("score", details if isinstance(details, float) else 0)
        weight_val = details.get("weight", 0.07)
        cat_data.append([
            cat.replace("_", " ").title(),
            f"{score_val:.0%}",
            f"{weight_val:.0%}"
        ])

    if len(cat_data) > 1:
        cat_table = Table(cat_data, colWidths=[2*inch, 1.5*inch, 1*inch])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ]))
        story.append(cat_table)
    story.append(Spacer(1, 12))

    if highlighted_sections:
        story.append(Paragraph("Highlighted Sections", section_style))
        story.append(Paragraph(
            "The following sections show characteristics associated with AI-generated text:",
            body_style
        ))
        for h in highlighted_sections[:10]:
            reason = h.get("reason", "Pattern match")
            snippet = h.get("snippet", "")
            story.append(Paragraph(
                f"<b>Reason:</b> {reason}<br/>"
                f"<i>\"{snippet[:300]}\"</i>",
                body_style
            ))
            story.append(Spacer(1, 4))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Paragraph(
        "This report was generated by an AI detection tool. "
        "It is intended as an analytical aid, not as definitive evidence. "
        "Always consult a human reviewer for final judgment.",
        disclaimer_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
