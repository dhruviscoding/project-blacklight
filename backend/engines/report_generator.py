from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
import base64
from datetime import datetime


# ---- Color palette (Blacklight brand) ----
COLOR_ACCENT = colors.HexColor("#D97757")
COLOR_DANGER = colors.HexColor("#DC2626")
COLOR_WARNING = colors.HexColor("#D97706")
COLOR_SUCCESS = colors.HexColor("#16A34A")
COLOR_TEXT = colors.HexColor("#1A1A1A")
COLOR_MUTED = colors.HexColor("#6B6563")
COLOR_BORDER = colors.HexColor("#E8E5E0")
COLOR_SURFACE = colors.HexColor("#F5F4F0")


def get_verdict_color(verdict: str):
    if "CONFIRMED" in verdict and "AI" in verdict:
        return COLOR_DANGER
    if "AI GENERATED" in verdict or "LIKELY AI" in verdict:
        return COLOR_DANGER if "AI GENERATED" in verdict else COLOR_WARNING
    if "AUTHENTIC" in verdict:
        return COLOR_SUCCESS
    return COLOR_MUTED


def get_risk_color(risk: str):
    mapping = {
        "CRITICAL": COLOR_DANGER,
        "HIGH": COLOR_WARNING,
        "MEDIUM": colors.HexColor("#D97706"),
        "LOW": COLOR_SUCCESS,
        "UNKNOWN": COLOR_MUTED
    }
    return mapping.get(risk, COLOR_MUTED)


def generate_pdf_report(analysis_result: dict, filename: str, media_type: str) -> bytes:
    """
    Generates a professional PDF forensic report from analysis results.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=22,
        fontName="Helvetica-Bold",
        textColor=COLOR_TEXT,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=COLOR_MUTED,
        spaceAfter=2
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=COLOR_MUTED,
        spaceBefore=12,
        spaceAfter=6,
        letterSpacing=1
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=COLOR_TEXT,
        spaceAfter=4,
        leading=14
    )

    mono_style = ParagraphStyle(
        "Mono",
        parent=styles["Normal"],
        fontSize=8,
        fontName="Courier",
        textColor=COLOR_TEXT,
        spaceAfter=2
    )

    verdict_style = ParagraphStyle(
        "Verdict",
        parent=styles["Normal"],
        fontSize=18,
        fontName="Helvetica-Bold",
        textColor=COLOR_TEXT,
        spaceAfter=4
    )

    story = []

    # ---- COVER / HEADER ----
    story.append(Paragraph("PROJECT BLACKLIGHT", ParagraphStyle(
        "Brand",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=COLOR_ACCENT,
        letterSpacing=2,
        spaceAfter=8
    )))

    story.append(Paragraph("Forensic Analysis Report", title_style))
    story.append(Paragraph(f"File: {filename}", subtitle_style))
    story.append(Paragraph(f"Media type: {media_type}", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
    story.append(Spacer(1, 6*mm))

    # ---- VERDICT SECTION ----
    verdict_data = analysis_result.get("verdict", {})
    if verdict_data:
        story.append(Paragraph("VERDICT", section_header_style))

        verdict_text = verdict_data.get("verdict", "UNKNOWN")
        confidence = verdict_data.get("confidence")
        risk = verdict_data.get("risk_level", "UNKNOWN")
        verdict_color = get_verdict_color(verdict_text)

        verdict_table_data = [
            [
                Paragraph(verdict_text, ParagraphStyle(
                    "VerdictBig",
                    parent=styles["Normal"],
                    fontSize=16,
                    fontName="Helvetica-Bold",
                    textColor=verdict_color
                )),
                Paragraph(
                    f"{confidence*100:.1f}%" if confidence else "N/A",
                    ParagraphStyle(
                        "Confidence",
                        parent=styles["Normal"],
                        fontSize=24,
                        fontName="Helvetica-Bold",
                        textColor=verdict_color,
                        alignment=TA_RIGHT
                    )
                )
            ]
        ]

        verdict_table = Table(verdict_table_data, colWidths=["70%", "30%"])
        verdict_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_SURFACE),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 3*mm))

        # Risk + flags row
        flags = []
        flags.append(f"Risk: {risk}")
        if verdict_data.get("decisive_signal"):
            flags.append(f"Decisive signal: {verdict_data['decisive_signal']}")
        if verdict_data.get("conflict_detected"):
            flags.append("Conflict detected")
        if verdict_data.get("coverage_warning"):
            flags.append("Low signal coverage")

        story.append(Paragraph(" · ".join(flags), ParagraphStyle(
            "Flags",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=get_risk_color(risk)
        )))
        story.append(Spacer(1, 2*mm))

        if verdict_data.get("summary"):
            story.append(Paragraph(verdict_data["summary"], body_style))

        story.append(Spacer(1, 6*mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 4*mm))

    # ---- SIGNAL BREAKDOWN ----
    signals = analysis_result.get("signals", {})
    if signals:
        story.append(Paragraph("SIGNAL BREAKDOWN", section_header_style))

        signal_table_data = [["Signal", "Category", "Score", "Finding"]]
        for key, signal in signals.items():
            if not signal or not isinstance(signal, dict) or "name" not in signal:
                continue
            score = signal.get("score")
            score_str = f"{score*100:.0f}%" if score is not None else "N/A"
            finding = signal.get("finding", "")
            if len(finding) > 80:
                finding = finding[:77] + "..."
            signal_table_data.append([
                Paragraph(signal.get("name", key), mono_style),
                Paragraph(signal.get("category", ""), body_style),
                Paragraph(score_str, ParagraphStyle(
                    "Score",
                    parent=styles["Normal"],
                    fontSize=9,
                    fontName="Helvetica-Bold",
                    textColor=COLOR_DANGER if score and score > 0.6 else COLOR_SUCCESS if score and score < 0.35 else COLOR_MUTED
                )),
                Paragraph(finding, ParagraphStyle(
                    "Finding",
                    parent=styles["Normal"],
                    fontSize=8,
                    fontName="Helvetica",
                    textColor=COLOR_MUTED
                ))
            ])

        signal_table = Table(signal_table_data, colWidths=["25%", "15%", "10%", "50%"])
        signal_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_SURFACE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_MUTED),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_SURFACE]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(signal_table)
        story.append(Spacer(1, 6*mm))

    # ---- METADATA ----
    metadata_signal = signals.get("metadata", {}) if signals else {}
    raw_data = metadata_signal.get("raw_data", {}) if metadata_signal else {}

    if raw_data:
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("METADATA", section_header_style))

        exif = raw_data.get("exif", {})
        gps = raw_data.get("gps", {})
        timestamps = raw_data.get("timestamps", {})
        tampering = raw_data.get("tampering", {})

        if tampering and tampering.get("software_detected"):
            story.append(Paragraph(
                f"Software detected: {tampering['software_detected']}" +
                (" (AI tool)" if tampering.get("ai_tool_match") else ""),
                ParagraphStyle("SoftwareTag", parent=body_style,
                               textColor=COLOR_DANGER if tampering.get("ai_tool_match") else COLOR_TEXT)
            ))

        if gps and gps.get("has_gps"):
            story.append(Paragraph(
                f"GPS: {gps['latitude']}, {gps['longitude']}" +
                (f" · Altitude: {gps['altitude']}m" if gps.get("altitude") else ""),
                body_style
            ))

        if timestamps:
            ts_data = [["Field", "Value"]]
            for label, key in [
                ("Date Original", "date_original"),
                ("Date Digitized", "date_digitized"),
                ("File Modified", "file_modify_date"),
                ("File Created", "file_create_date")
            ]:
                if timestamps.get(key):
                    ts_data.append([label, timestamps[key]])

            if len(ts_data) > 1:
                ts_table = Table(ts_data, colWidths=["30%", "70%"])
                ts_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_SURFACE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(ts_table)

        if exif:
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph("EXIF Fields", ParagraphStyle(
                "SubHeader", parent=body_style, fontName="Helvetica-Bold"
            )))
            exif_data = [["Field", "Value"]]
            for k, v in list(exif.items())[:20]:
                exif_data.append([str(k), str(v)[:80]])
            exif_table = Table(exif_data, colWidths=["35%", "65%"])
            exif_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_SURFACE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, 1), (0, -1), "Courier"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_SURFACE]),
                ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(exif_table)

        story.append(Spacer(1, 6*mm))

    # ---- HASHES ----
    hashes = analysis_result.get("signals", {}).get("hashes", {}) if analysis_result.get("signals") else {}
    crypto = hashes.get("cryptographic", {}) if hashes else {}
    perceptual = hashes.get("perceptual", {}) if hashes else {}

    if crypto or perceptual:
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("FILE INTEGRITY — HASHES", section_header_style))

        hash_data = [["Algorithm", "Hash Value"]]
        if crypto:
            for algo, value in crypto.items():
                hash_data.append([algo.upper(), value])
        if perceptual:
            for algo, value in perceptual.items():
                hash_data.append([algo, value])

        hash_table = Table(hash_data, colWidths=["15%", "85%"])
        hash_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), COLOR_SURFACE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 1), (-1, -1), "Courier"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_SURFACE]),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(hash_table)
        story.append(Spacer(1, 6*mm))

    # ---- C2PA ----
    c2pa = analysis_result.get("signals", {}).get("c2pa", {}) if analysis_result.get("signals") else {}
    if c2pa and c2pa.get("has_c2pa"):
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_BORDER))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph("C2PA CONTENT CREDENTIALS", section_header_style))
        story.append(Paragraph(c2pa.get("finding", ""), ParagraphStyle(
            "C2PAFinding", parent=body_style,
            textColor=COLOR_DANGER if c2pa.get("score", 0) > 0.9 else COLOR_SUCCESS
        )))
        story.append(Spacer(1, 6*mm))

    # ---- FOOTER ----
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Generated by Project Blacklight · AI-Generated Media Forensics Platform · "
        "This report is for investigative purposes. All findings should be verified by a qualified forensic analyst.",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=7,
            fontName="Helvetica",
            textColor=COLOR_MUTED,
            alignment=TA_CENTER
        )
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()