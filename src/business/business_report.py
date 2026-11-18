"""Downloadable report for the Business Dashboard.

The HTML report needs no extra packages: it is one self-contained file with simple
charts that opens in any browser (and can be saved as PDF with Print). A real PDF
file is also produced when the optional 'reportlab' package is installed.
"""

import html
import io
import re
from datetime import datetime

import pandas as pd

from src.business.business_engine import fmt_number, fmt_pct

_SEVERITY_TEXT = {"high": "Urgent", "medium": "Look at this", "info": "Good to know"}
_SEVERITY_COLOR = {"high": "#b3261e", "medium": "#a15c00", "info": "#1f5fa8"}


def pdf_available():
    try:
        import reportlab  # noqa: F401
        return True
    except ImportError:
        return False


# --------------------------------------------------------------------------
# Shared preparation
# --------------------------------------------------------------------------

def _clean_labels(series):
    """Drop the '1-' sort prefix used for weekday labels in the on-screen charts."""
    if series is None or len(series) == 0:
        return series
    cleaned = series.copy()
    cleaned.index = [re.sub(r"^\d-", "", str(name)) for name in cleaned.index]
    return cleaned


def _ai_parts(ai_result):
    """Pull the readable AI text out of a generate_generic_insights() result."""
    if not ai_result:
        return None
    insights = ai_result.get("insights")
    if not isinstance(insights, dict):
        return None

    summary = insights.get("executive_summary")
    recs = insights.get("business_recommendations")
    return {
        "summary": summary.get("text", "") if isinstance(summary, dict) else "",
        "recommendations": [
            {
                "action": str(r.get("action", "")),
                "reason": str(r.get("reason", "")),
                "caveat": str(r.get("caveat", "")),
            }
            for r in (recs if isinstance(recs, list) else [])
            if isinstance(r, dict)
        ],
    }


def _kpi_rows(kpis, comparison, metric_label):
    """[(label, value text, change text or '')]"""
    changes = comparison["change_pct"] if comparison else {}
    rows = [
        (f"Total {metric_label.lower()}", fmt_number(kpis["revenue"]), fmt_pct(changes.get("revenue")) if changes.get("revenue") is not None else ""),
        ("Orders", fmt_number(kpis["orders"]), fmt_pct(changes.get("orders")) if changes.get("orders") is not None else ""),
        ("Average per order", fmt_number(kpis["average_order_value"]), fmt_pct(changes.get("average_order_value")) if changes.get("average_order_value") is not None else ""),
    ]
    if "units_sold" in kpis:
        rows.append(("Units sold", fmt_number(kpis["units_sold"]), fmt_pct(changes.get("units_sold")) if changes.get("units_sold") is not None else ""))
    return rows


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

def _svg_bars(series, color="#2f6fbd", width=640, row_height=26):
    """Horizontal bar chart as inline SVG."""
    if series is None or len(series) == 0:
        return ""
    values = [float(v) for v in series.values]
    maximum = max(max(values), 1e-9)
    label_width, value_width = 170, 90
    bar_area = width - label_width - value_width
    height = row_height * len(values) + 8
    parts = [f'<svg viewBox="0 0 {width} {height}" width="100%" role="img">']
    for i, (name, value) in enumerate(zip(series.index, values)):
        y = 4 + i * row_height
        bar = max(0.0, value) / maximum * bar_area
        parts.append(
            f'<text x="0" y="{y + 17}" font-size="13" fill="#333">{html.escape(str(name)[:24])}</text>'
            f'<rect x="{label_width}" y="{y + 4}" width="{bar:.1f}" height="{row_height - 10}" rx="3" fill="{color}"/>'
            f'<text x="{label_width + bar + 6:.1f}" y="{y + 17}" font-size="12" fill="#555">{fmt_number(value)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _svg_line(series, color="#2f6fbd", width=640, height=190):
    """Line chart as inline SVG."""
    if series is None or len(series) < 2:
        return ""
    values = [float(v) for v in series.values]
    low, high = min(values + [0.0]), max(values)
    span = (high - low) or 1.0
    left, right, top, bottom = 8, 8, 10, 24
    plot_w, plot_h = width - left - right, height - top - bottom
    points = []
    for i, value in enumerate(values):
        x = left + plot_w * i / (len(values) - 1)
        y = top + plot_h * (1 - (value - low) / span)
        points.append(f"{x:.1f},{y:.1f}")
    first, last = pd.Timestamp(series.index[0]), pd.Timestamp(series.index[-1])
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" role="img">'
        f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" stroke="#ccc"/>'
        f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(points)}"/>'
        f'<text x="{left}" y="{height - 6}" font-size="12" fill="#555">{first:%b %d, %Y}</text>'
        f'<text x="{width - right}" y="{height - 6}" font-size="12" fill="#555" text-anchor="end">{last:%b %d, %Y}</text>'
        f'<text x="{width - right}" y="{top + 10}" font-size="12" fill="#555" text-anchor="end">peak {fmt_number(max(values))}</text>'
        "</svg>"
    )


def build_report_html(
    title,
    summary_lines,
    kpis,
    comparison,
    periods,
    alerts,
    metric_label="Revenue",
    time_series=None,
    time_unit="",
    charts=None,
    ai_result=None,
    filters_text="",
):
    """Return one self-contained HTML document as a string."""
    esc = html.escape
    ai = _ai_parts(ai_result)
    out = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"<title>{esc(title)}</title>",
        "<style>"
        "body{font-family:Segoe UI,Arial,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;color:#222;line-height:1.5}"
        "h1{margin-bottom:0}h2{margin-top:32px;border-bottom:1px solid #ddd;padding-bottom:4px}"
        ".muted{color:#666;font-size:14px}"
        ".kpis{display:flex;flex-wrap:wrap;gap:12px}.kpi{flex:1 1 150px;border:1px solid #ddd;border-radius:8px;padding:10px 14px}"
        ".kpi b{display:block;font-size:22px}.up{color:#1b7a3d}.down{color:#b3261e}"
        ".alert{border-left:4px solid #999;padding:6px 12px;margin:10px 0;background:#fafafa}"
        "@media print{body{margin:0}}"
        "</style></head><body>",
        f"<h1>{esc(title)}</h1>",
        f"<p class='muted'>Created {datetime.now():%b %d, %Y %H:%M}"
        f"{' · ' + esc(filters_text) if filters_text else ''}</p>",
        "<h2>What happened</h2><ul>",
    ]
    out += [f"<li>{esc(line)}</li>" for line in summary_lines]
    out.append("</ul>")

    out.append("<h2>Key numbers</h2><div class='kpis'>")
    for label, value, change in _kpi_rows(kpis, comparison, metric_label):
        css = ""
        if change:
            css = "up" if change.startswith("+") else "down"
        out.append(
            f"<div class='kpi'><span class='muted'>{esc(label)}</span><b>{esc(value)}</b>"
            f"{f'<span class={css}>{esc(change)} vs previous period</span>' if change else ''}</div>"
        )
    out.append("</div>")
    if periods:
        out.append(
            f"<p class='muted'>Latest period: {esc(periods['current_label'])}. "
            f"Previous period: {esc(periods['previous_label'])}.</p>"
        )

    if alerts:
        out.append("<h2>Things to look at</h2>")
        for alert in alerts:
            color = _SEVERITY_COLOR[alert["severity"]]
            out.append(
                f"<div class='alert' style='border-color:{color}'><b style='color:{color}'>"
                f"{esc(_SEVERITY_TEXT[alert['severity']])}:</b> <b>{esc(alert['title'])}</b><br>"
                f"{esc(alert['detail'])}</div>"
            )

    if time_series is not None and len(time_series) >= 2:
        out.append(f"<h2>{esc(metric_label)} over time (by {esc(time_unit)})</h2>")
        out.append(_svg_line(time_series))

    for heading, series in (charts or {}).items():
        chart = _svg_bars(_clean_labels(series))
        if chart:
            out.append(f"<h2>{esc(heading)}</h2>{chart}")

    if ai:
        out.append("<h2>Explained in plain words (AI)</h2>")
        if ai["summary"]:
            out.append(f"<p>{esc(ai['summary'])}</p>")
        if ai["recommendations"]:
            out.append("<h3>What you could do</h3><ul>")
            for rec in ai["recommendations"]:
                out.append(
                    f"<li><b>{esc(rec['action'])}</b><br><span class='muted'>Why: {esc(rec['reason'])}"
                    f"{' · Keep in mind: ' + esc(rec['caveat']) if rec['caveat'] else ''}</span></li>"
                )
            out.append("</ul>")
        out.append("<p class='muted'>AI-written text can contain mistakes. Check important numbers against the tables above.</p>")

    out.append("</body></html>")
    return "".join(out)


# --------------------------------------------------------------------------
# PDF (optional: needs reportlab)
# --------------------------------------------------------------------------

def build_report_pdf(
    title,
    summary_lines,
    kpis,
    comparison,
    periods,
    alerts,
    metric_label="Revenue",
    charts=None,
    ai_result=None,
    filters_text="",
):
    """Return PDF bytes, or None when reportlab is not installed."""
    if not pdf_available():
        return None

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    esc = html.escape
    styles = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#666666"))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm, title=title)
    story = [
        Paragraph(esc(title), styles["Title"]),
        Paragraph(f"Created {datetime.now():%b %d, %Y %H:%M}{' · ' + esc(filters_text) if filters_text else ''}", small),
        Spacer(1, 10),
        Paragraph("What happened", styles["Heading2"]),
    ]
    for line in summary_lines:
        story.append(Paragraph("• " + esc(line), styles["BodyText"]))

    story.append(Paragraph("Key numbers", styles["Heading2"]))
    rows = [["", "Value", "Change vs previous period"]]
    for label, value, change in _kpi_rows(kpis, comparison, metric_label):
        rows.append([label, value, change or "-"])
    table = Table(rows, colWidths=[6 * cm, 4 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    if periods:
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"Latest period: {esc(periods['current_label'])}. Previous period: {esc(periods['previous_label'])}.", small))

    if alerts:
        story.append(Paragraph("Things to look at", styles["Heading2"]))
        for alert in alerts:
            story.append(Paragraph(
                f"<b>{esc(_SEVERITY_TEXT[alert['severity']])}: {esc(alert['title'])}</b><br/>{esc(alert['detail'])}",
                styles["BodyText"]))
            story.append(Spacer(1, 4))

    for heading, series in (charts or {}).items():
        if series is None or len(series) == 0:
            continue
        series = _clean_labels(series)
        story.append(Paragraph(esc(heading), styles["Heading2"]))
        data = [["Name", metric_label]] + [[str(k)[:40], fmt_number(v)] for k, v in series.items()]
        chart_table = Table(data, colWidths=[9 * cm, 5 * cm])
        chart_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eeeeee")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(chart_table)

    ai = _ai_parts(ai_result)
    if ai:
        story.append(Paragraph("Explained in plain words (AI)", styles["Heading2"]))
        if ai["summary"]:
            story.append(Paragraph(esc(ai["summary"]), styles["BodyText"]))
        for rec in ai["recommendations"]:
            story.append(Paragraph(
                f"• <b>{esc(rec['action'])}</b> - why: {esc(rec['reason'])}"
                f"{'. Keep in mind: ' + esc(rec['caveat']) if rec['caveat'] else ''}", styles["BodyText"]))
        story.append(Paragraph("AI-written text can contain mistakes. Check important numbers against the tables.", small))

    doc.build(story)
    return buffer.getvalue()
