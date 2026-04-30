"""
Jim Appiah's AI Development Framework — PDF report generator
Builds a polished, McKinsey-styled client-facing report using reportlab.
"""
import io
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.patches import Wedge
import numpy as np

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

matplotlib.use("Agg")  # non-interactive backend

# ---------------------------------------------------------------------------
# BRAND PALETTE
# ---------------------------------------------------------------------------
NAVY = colors.HexColor("#1B365D")
NAVY_LIGHT = colors.HexColor("#2E5A87")
GOLD = colors.HexColor("#C9A961")
CHARCOAL = colors.HexColor("#1B1B1B")
GREY = colors.HexColor("#6B6B6B")
LIGHT_GREY = colors.HexColor("#E8E8E5")
CREAM = colors.HexColor("#F5F5F0")


# ---------------------------------------------------------------------------
# CHART HELPERS — return BytesIO PNG for embedding in PDF
# ---------------------------------------------------------------------------
def _radar_chart(stage_scores: dict) -> io.BytesIO:
    """Five-axis radar chart of stage scores."""
    labels = ["WHY\nStrategic\nImperative", "WHERE\nValue Pools",
              "WHAT\nUse Case Fit", "HOW\nCapability", "SO WHAT\nROI"]
    keys = ["why", "where", "what", "how", "so_what"]
    values = [stage_scores[k] for k in keys]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5.2, 5.2), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(angles, values, color="#1B365D", linewidth=2.2)
    ax.fill(angles, values, color="#1B365D", alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9, color="#1B1B1B")
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], fontsize=7, color="#6B6B6B")
    ax.grid(color="#E8E8E5", linewidth=0.8)
    ax.spines["polar"].set_color("#E8E8E5")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _gauge_chart(score: float, color_hex: str) -> io.BytesIO:
    """Half-circle gauge of composite score."""
    fig, ax = plt.subplots(figsize=(5.5, 3.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_aspect("equal")
    ax.axis("off")

    # Background arc
    bg = Wedge((0.5, 0), 0.42, 0, 180, width=0.10,
               facecolor="#E8E8E5", edgecolor="none")
    ax.add_patch(bg)

    # Score arc
    angle = 180 * (score / 100)
    fg = Wedge((0.5, 0), 0.42, 180 - angle, 180, width=0.10,
               facecolor=color_hex, edgecolor="none")
    ax.add_patch(fg)

    # Score text
    ax.text(0.5, 0.10, f"{int(round(score))}",
            ha="center", va="bottom", fontsize=44,
            color=color_hex, fontweight="bold")
    ax.text(0.5, 0.02, "out of 100",
            ha="center", va="bottom", fontsize=10, color="#6B6B6B")

    ax.set_xlim(0, 1)
    ax.set_ylim(-0.05, 0.55)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _capability_bar_chart(layer_scores: dict) -> io.BytesIO:
    """Horizontal bar chart of capability layer scores."""
    layers = list(layer_scores.keys())
    scores = list(layer_scores.values())
    min_score = min(scores)

    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y_pos = np.arange(len(layers))
    # Bottleneck (lowest score) is always gold; everything else navy variants.
    bar_colors = []
    for s in scores:
        if s == min_score:
            bar_colors.append("#C9A961")  # gold = bottleneck
        elif s >= 4:
            bar_colors.append("#1B365D")  # navy = strong
        else:
            bar_colors.append("#2E5A87")  # navy-light = adequate

    ax.barh(y_pos, scores, color=bar_colors, height=0.55)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(layers, fontsize=10, color="#1B1B1B")
    ax.invert_yaxis()
    ax.set_xlim(0, 5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["1", "2", "3", "4", "5"], fontsize=9, color="#6B6B6B")
    ax.set_xlabel("Score (1–5)", fontsize=9, color="#6B6B6B")

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#E8E8E5")
    ax.spines["bottom"].set_color("#E8E8E5")
    ax.tick_params(colors="#6B6B6B")

    # Add value labels at end of bars
    for i, v in enumerate(scores):
        ax.text(v + 0.08, i, f"{v}", va="center", fontsize=9, color="#1B1B1B")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# REPORT BUILDER
# ---------------------------------------------------------------------------
def _styles():
    """Custom paragraph styles."""
    base = getSampleStyleSheet()
    return {
        "brand": ParagraphStyle(
            "brand", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=10, textColor=GOLD, leading=12, alignment=TA_LEFT,
        ),
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, textColor=NAVY, leading=28, spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=12, textColor=GREY, leading=16, spaceAfter=18,
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=14, textColor=NAVY, leading=18, spaceBefore=14,
            spaceAfter=8, alignment=TA_LEFT,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=11, textColor=NAVY, leading=14, spaceBefore=10,
            spaceAfter=4, alignment=TA_LEFT,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, textColor=CHARCOAL, leading=14, spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "callout": ParagraphStyle(
            "callout", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, textColor=NAVY, leading=14, leftIndent=10,
            rightIndent=10, spaceAfter=8, spaceBefore=4,
        ),
        "verdict": ParagraphStyle(
            "verdict", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=15, textColor=colors.white, leading=20,
            alignment=TA_CENTER,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontName="Helvetica",
            fontSize=8.5, textColor=GREY, leading=11,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, textColor=GREY, leading=10, alignment=TA_CENTER,
        ),
    }


def _header_footer(canvas, doc, contact_email: str):
    """Page header and footer drawn on every page."""
    canvas.saveState()
    width, height = LETTER

    # Top accent rule
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.5)
    canvas.line(0.75 * inch, height - 0.5 * inch,
                width - 0.75 * inch, height - 0.5 * inch)

    # Brand mark in header
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(0.75 * inch, height - 0.38 * inch,
                      "JIM APPIAH'S AI DEVELOPMENT FRAMEWORK")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawRightString(width - 0.75 * inch, height - 0.38 * inch,
                           "AI READINESS DIAGNOSTIC")

    # Footer rule
    canvas.setStrokeColor(LIGHT_GREY)
    canvas.setLineWidth(0.4)
    canvas.line(0.75 * inch, 0.55 * inch,
                width - 0.75 * inch, 0.55 * inch)

    # Footer text
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(0.75 * inch, 0.38 * inch,
                      f"Generated {datetime.now().strftime('%B %d, %Y')}")
    canvas.drawCentredString(width / 2, 0.38 * inch,
                             "Confidential — for the named recipient only")
    canvas.drawRightString(width - 0.75 * inch, 0.38 * inch,
                           f"Page {doc.page}")
    if contact_email:
        canvas.setFillColor(NAVY)
        canvas.drawCentredString(width / 2, 0.24 * inch, contact_email)

    canvas.restoreState()


def _money(n: float) -> str:
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n/1_000:.0f}K"
    return f"${n:.0f}"


def build_pdf(assessment: dict, contact_email: str, calendly_url: str) -> bytes:
    """
    Build the full PDF report and return its bytes.
    `assessment` is the dict returned by scoring.full_assessment().
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        topMargin=0.85 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title="AI Readiness Diagnostic",
        author="Jim Appiah's AI Development Framework",
    )
    s = _styles()
    story = []

    lead = assessment["lead"]
    archetype = assessment["archetype"]
    verdict = assessment["verdict"]
    composite = assessment["composite"]
    stage_scores = assessment["stage_scores"]
    roi = assessment["roi"]

    # =========================================================
    # COVER
    # =========================================================
    story.append(Paragraph("AI READINESS DIAGNOSTIC", s["brand"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Prepared for {lead.get('company', '—')}",
        s["title"]
    ))
    story.append(Paragraph(
        f"{lead.get('name', '—')} &nbsp;·&nbsp; "
        f"{assessment['industry']} &nbsp;·&nbsp; "
        f"{datetime.now().strftime('%B %Y')}",
        s["subtitle"]
    ))

    # Verdict banner
    verdict_table = Table(
        [[Paragraph(verdict["label"], s["verdict"])]],
        colWidths=[7.0 * inch],
    )
    verdict_color = colors.HexColor(verdict["color"])
    verdict_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 14))

    # Composite gauge + summary side by side
    gauge = Image(_gauge_chart(composite, verdict["color"]),
                  width=2.8 * inch, height=1.6 * inch)
    summary_para = Paragraph(verdict["summary"], s["body"])

    cover_table = Table([[gauge, summary_para]], colWidths=[2.9 * inch, 4.1 * inch])
    cover_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (1, 0), (1, 0), 12),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 14))

    # Industry archetype callout
    story.append(Paragraph("INDUSTRY ARCHETYPE", s["h2"]))
    archetype_table = Table([[
        Paragraph(
            f"<b>{archetype['name']}</b><br/>"
            f"<font color='#6B6B6B'>{archetype['tagline']}</font>",
            s["body"],
        ),
    ]], colWidths=[7.0 * inch])
    archetype_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, 0), 3, GOLD),
    ]))
    story.append(archetype_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph(archetype["description"], s["body"]))

    story.append(PageBreak())

    # =========================================================
    # PAGE 2 — STAGE-BY-STAGE SCORES
    # =========================================================
    story.append(Paragraph("Stage-by-Stage Readiness", s["h1"]))
    story.append(Paragraph(
        "Your composite score is a weighted average of five strategic questions. "
        "Scoring each stage separately reveals the specific lever to pull next.",
        s["body"]
    ))
    story.append(Spacer(1, 10))

    radar = Image(_radar_chart(stage_scores), width=3.5 * inch, height=3.5 * inch)

    # Build stage score table
    stage_data = [
        ["", "Stage", "Score", "Read"],
        ["1", "WHY — Strategic Imperative", f"{stage_scores['why']}",
         _read(stage_scores['why'])],
        ["2", "WHERE — Value Pools", f"{stage_scores['where']}",
         _read(stage_scores['where'])],
        ["3", "WHAT — Use Case Fit", f"{stage_scores['what']}",
         _read(stage_scores['what'])],
        ["4", "HOW — Capability Stack", f"{stage_scores['how']}",
         _read(stage_scores['how'])],
        ["5", "SO WHAT — ROI Outlook", f"{stage_scores['so_what']}",
         _read(stage_scores['so_what'])],
    ]
    stage_table = Table(stage_data, colWidths=[0.25 * inch, 1.85 * inch,
                                                0.55 * inch, 0.85 * inch])
    stage_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GREY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, NAVY),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("TEXTCOLOR", (0, 1), (-1, -1), CHARCOAL),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 1), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (2, 1), (2, -1), NAVY),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, LIGHT_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
    ]))

    page2_table = Table([[radar, stage_table]], colWidths=[3.6 * inch, 3.4 * inch])
    page2_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(page2_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 3 — CAPABILITY DIAGNOSTIC
    # =========================================================
    story.append(Paragraph("Capability Stack Diagnostic", s["h1"]))
    story.append(Paragraph(
        "The capability stack determines whether AI investment will land. "
        "Your weakest layer caps the entire stack — you cannot exceed your bottleneck.",
        s["body"]
    ))
    story.append(Spacer(1, 8))

    cap_chart = Image(_capability_bar_chart(assessment["layer_scores"]),
                      width=6.5 * inch, height=3.1 * inch)
    story.append(cap_chart)
    story.append(Spacer(1, 12))

    # Bottleneck callout
    bottleneck_text = (
        f"<b>Your bottleneck: {assessment['weakest_layer']}.</b> "
        f"Closing this gap is the single highest-leverage move before "
        f"scaling AI investment further."
    )
    bottleneck_table = Table([[Paragraph(bottleneck_text, s["body"])]],
                              colWidths=[7.0 * inch])
    bottleneck_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, 0), 3, GOLD),
    ]))
    story.append(bottleneck_table)
    story.append(Spacer(1, 16))

    # =========================================================
    # PAGE 3 cont. — VALUE POOLS
    # =========================================================
    story.append(Paragraph("Value Pools at Stake", s["h1"]))
    story.append(Paragraph(
        "Where in your business is AI value most concentrated? These are the "
        "areas to focus first — not because they're easiest, but because they "
        "represent the largest prize.",
        s["body"]
    ))
    story.append(Spacer(1, 6))

    pool_rows = [["Rank", "Value Pool", "Stake"]]
    score_label = {0: "Not relevant", 1: "Low", 2: "Medium", 3: "High"}
    for i, p in enumerate(assessment["ranked_pools"][:5], 1):
        pool_rows.append([str(i), p["label"], score_label.get(p["score"], "—")])

    pool_table = Table(pool_rows, colWidths=[0.6 * inch, 4.4 * inch, 2.0 * inch])
    pool_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GREY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, NAVY),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TEXTCOLOR", (0, 1), (-1, -1), CHARCOAL),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, LIGHT_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 7),
    ]))
    story.append(pool_table)

    story.append(PageBreak())

    # =========================================================
    # PAGE 4 — RECOMMENDED USE CASES
    # =========================================================
    story.append(Paragraph("Recommended Use Cases", s["h1"]))
    story.append(Paragraph(
        f"Based on your archetype ({archetype['name']}) and your scoring, "
        f"these use cases offer the strongest combination of strategic value "
        f"and feasibility for your business right now.",
        s["body"]
    ))
    story.append(Spacer(1, 8))

    top_use_cases = assessment["ranked_use_cases"][:3]
    for i, uc in enumerate(top_use_cases, 1):
        uc_table = Table([[
            Paragraph(f"<b>0{i}</b>", ParagraphStyle(
                "num", fontName="Helvetica-Bold", fontSize=18, textColor=GOLD,
            )),
            Paragraph(
                f"<b>{uc['label']}</b><br/>"
                f"<font color='#6B6B6B' size='8'>"
                f"Strategic fit score: {uc['score']}/5</font>",
                s["body"],
            ),
        ]], colWidths=[0.6 * inch, 6.4 * inch])
        uc_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), CREAM),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(uc_table)
        story.append(Spacer(1, 8))

    # Key risks for archetype
    story.append(Spacer(1, 8))
    story.append(Paragraph("Risks to Manage", s["h2"]))
    risks_text = "<br/>".join(f"• {r}" for r in archetype["key_risks"])
    story.append(Paragraph(risks_text, s["body"]))

    story.append(PageBreak())

    # =========================================================
    # PAGE 5 — ROI OUTLOOK
    # =========================================================
    story.append(Paragraph("ROI Outlook (18-Month Horizon)", s["h1"]))
    story.append(Paragraph(
        "Indicative figures based on your inputs and archetype benchmarks. "
        "Real engagements refine these with your actual cost base, baseline "
        "metrics, and capture-rate assumptions.",
        s["body"]
    ))
    story.append(Spacer(1, 12))

    roi_data = [
        ["Annual Revenue", _money(roi["revenue"])],
        ["AI Value at Stake", f"{roi['value_pct']*100:.1f}% of revenue · "
                              f"{_money(roi['theoretical_value'])}"],
        ["Capture Rate (18-mo)", f"{roi['capture_rate']*100:.0f}%"],
        ["Captured Value", _money(roi["captured_value"])],
        ["AI Investment", _money(roi["investment"])],
        ["Net Value", _money(roi["net_value"])],
        ["ROI Multiple", f"{roi['roi_multiple']:.1f}×"],
        ["Payback", f"{roi['payback_months']:.0f} months"
            if roi["payback_months"] != float("inf") else "n/a"],
    ]
    roi_table = Table(roi_data, colWidths=[2.5 * inch, 4.5 * inch])
    roi_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), GREY),
        ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, LIGHT_GREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.append(roi_table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "<i>Note: These figures assume disciplined execution and exclude "
        "one-time transformation costs. The single biggest variable is "
        "capture rate, which is determined by your operating model and "
        "adoption — not by the AI itself.</i>",
        s["small"],
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 6 — RECOMMENDED NEXT STEPS + CTA
    # =========================================================
    story.append(Paragraph("Recommended Next Steps", s["h1"]))
    for i, step in enumerate(verdict["next_steps"], 1):
        step_table = Table([[
            Paragraph(f"<b>0{i}</b>", ParagraphStyle(
                "num2", fontName="Helvetica-Bold", fontSize=14, textColor=GOLD,
            )),
            Paragraph(step, s["body"]),
        ]], colWidths=[0.5 * inch, 6.5 * inch])
        step_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(step_table)
        story.append(Spacer(1, 4))

    # First move callout (white text on navy background)
    story.append(Spacer(1, 14))
    story.append(Paragraph("Your First Move", s["h2"]))
    first_move_style = ParagraphStyle(
        "fm", fontName="Helvetica-Oblique", fontSize=11,
        textColor=colors.white, leading=15,
    )
    first_move_table = Table(
        [[Paragraph(archetype["first_move"], first_move_style)]],
        colWidths=[7.0 * inch],
    )
    first_move_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(first_move_table)

    # CTA
    story.append(Spacer(1, 24))
    story.append(Paragraph("Continue the Conversation", s["h1"]))
    cta_text = (
        "This diagnostic is the start, not the answer. The next step is a "
        "30-minute discovery call to translate this report into a concrete "
        "first project — sized to your business, sequenced to your readiness."
    )
    story.append(Paragraph(cta_text, s["body"]))
    story.append(Spacer(1, 10))

    cta_lines = []
    if calendly_url:
        cta_lines.append(
            f"<b>Book a discovery call:</b> "
            f"<font color='#1B365D'>{calendly_url}</font>"
        )
    if contact_email:
        cta_lines.append(
            f"<b>Or reach out directly:</b> "
            f"<font color='#1B365D'>{contact_email}</font>"
        )
    for line in cta_lines:
        story.append(Paragraph(line, s["body"]))
        story.append(Spacer(1, 4))

    # ---- Build ----
    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, contact_email),
        onLaterPages=lambda c, d: _header_footer(c, d, contact_email),
    )
    return buf.getvalue()


def _read(score: float) -> str:
    """Short qualitative read of a 0-100 score."""
    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Solid"
    if score >= 35:
        return "Developing"
    return "Foundational"
