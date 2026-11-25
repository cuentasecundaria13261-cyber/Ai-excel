"""Small visual building blocks: icons, number cards, alert cards.

Everything is plain HTML with inline SVG icons (no images, no extra packages). All text that
comes from the data or from the visitor is escaped before it is placed in the HTML, and "$" is
written as an HTML entity so Streamlit never reads it as a maths formula.
"""

import html

import streamlit as st

# Simple stroke icons (24x24 grid).
_ICONS = {
    "upload": "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12",
    "download": "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    "chart": "M12 20V10M18 20V4M6 20v-4",
    "share": "M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13",
    "money": "M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
    "bag": "M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4zM3 6h18M16 10a4 4 0 0 1-8 0",
    "tag": "M20.6 13.4l-7.2 7.2a2 2 0 0 1-2.8 0L2 12V2h10l8.6 8.6a2 2 0 0 1 0 2.8zM7 7h.01",
    "box": "M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7zM3.3 7L12 12l8.7-5M12 22V12",
    "list": "M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
    "alert": "M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0zM12 9v4M12 17h.01",
    "info": "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 16v-4M12 8h.01",
    "check": "M20 6L9 17l-5-5",
    "up": "M23 6l-9.5 9.5-5-5L1 18M17 6h6v6",
    "down": "M23 18l-9.5-9.5-5 5L1 6M17 18h6v-6",
    "spark": "M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9zM19 16l.7 1.8L21.5 18.5l-1.8.7L19 21l-.7-1.8-1.8-.7 1.8-.7z",
    "table": "M3 3h18v18H3zM3 9h18M3 15h18M9 3v18",
}


def esc(text):
    """Safe for HTML and for Streamlit's markdown: no tags, no maths dollars."""
    return html.escape(str(text)).replace("$", "&#36;")


def icon(name, size=20):
    path = _ICONS.get(name, _ICONS["info"])
    return (
        f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
        f"stroke-width='2' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>"
        f"<path d='{path}'/></svg>"
    )


def kpi_cards_html(items):
    """items: list of dicts {label, value, icon, change (text or None), direction ('up'/'down'/None)}."""
    cards = []
    for item in items:
        change = item.get("change")
        chip = ""
        if change:
            direction = item.get("direction") or "flat"
            arrow = icon("up", 14) if direction == "up" else icon("down", 14) if direction == "down" else ""
            chip = f"<div class='chip {direction}'>{arrow}<span>{esc(change)}</span></div>"
        hint = f"<div class='kpi-hint'>{esc(item['hint'])}</div>" if item.get("hint") else ""
        cards.append(
            "<div class='kpi'>"
            f"<div class='kpi-icon'>{icon(item.get('icon', 'chart'), 20)}</div>"
            f"<div class='kpi-label'>{esc(item['label'])}</div>"
            f"<div class='kpi-value'>{esc(item['value'])}</div>"
            f"{hint}{chip}</div>"
        )
    return "<div class='kpis'>" + "".join(cards) + "</div>"


def render_kpi_cards(items):
    st.markdown(kpi_cards_html(items), unsafe_allow_html=True)


_ALERT_ICONS = {"high": "alert", "medium": "alert", "info": "info"}


def alert_card_html(severity, title, detail=""):
    severity = severity if severity in _ALERT_ICONS else "info"
    body = f"<div class='alert-detail'>{esc(detail)}</div>" if detail else ""
    return (
        f"<div class='alert-card {severity}'>"
        f"<div class='alert-icon'>{icon(_ALERT_ICONS[severity], 20)}</div>"
        f"<div><div class='alert-title'>{esc(title)}</div>{body}</div></div>"
    )


def render_alert_card(severity, title, detail=""):
    st.markdown(alert_card_html(severity, title, detail), unsafe_allow_html=True)


def ok_card_html(text):
    return (
        "<div class='alert-card ok'>"
        f"<div class='alert-icon'>{icon('check', 20)}</div>"
        f"<div><div class='alert-title'>{esc(text)}</div></div></div>"
    )


def render_ok_card(text):
    st.markdown(ok_card_html(text), unsafe_allow_html=True)


def summary_html(lines):
    """The first line is the headline; the rest are small supporting lines."""
    if not lines:
        return ""
    rest = "".join(f"<li>{esc(line)}</li>" for line in lines[1:])
    more = f"<ul>{rest}</ul>" if rest else ""
    return f"<div class='story'><div class='story-head'>{esc(lines[0])}</div>{more}</div>"


def render_summary(lines):
    st.markdown(summary_html(lines), unsafe_allow_html=True)


def section_title_html(text, icon_name):
    return f"<div class='section'><span class='section-icon'>{icon(icon_name, 18)}</span><span>{esc(text)}</span></div>"


def render_section(text, icon_name):
    st.markdown(section_title_html(text, icon_name), unsafe_allow_html=True)


def bar_chart_html(items, title="", hint=""):
    """Clean horizontal bars. items: list of (name, value, value_text) or (name, value, value_text, tip_lines).
    The longest bar is the biggest value. tip_lines are shown when the visitor hovers over a row."""
    import json
    items = list(items)[:12]
    top = max([item[1] for item in items if item[1] is not None] + [0]) or 1
    rows = []
    for item in items:
        name, value, text = item[0], item[1], item[2]
        tip = item[3] if len(item) > 3 and item[3] else None
        width = max(0.0, min(100.0, (value or 0) / top * 100))
        tip_attr = f" data-tip='{esc(json.dumps([name] + list(tip), ensure_ascii=False))}'" if tip else ""
        rows.append(
            f"<div class='bar-row'{tip_attr}>"
            f"<div class='bar-name' title='{esc(name)}'>{esc(name)}</div>"
            f"<div class='bar-track'><div class='bar-fill' style='width:{width:.1f}%'></div></div>"
            f"<div class='bar-value'>{esc(text)}</div></div>"
        )
    head = f"<div class='bar-title'>{esc(title)}</div>" if title else ""
    foot = f"<div class='bar-hint'>{icon('info', 16)}<span>{esc(hint)}</span></div>" if hint else ""
    return f"<div class='bars'>{head}{''.join(rows)}{foot}</div>"


def render_bar_chart(items, title="", hint=""):
    st.markdown(bar_chart_html(items, title, hint), unsafe_allow_html=True)


def ai_answer_html(headline):
    """The main AI answer, as one clean card."""
    return (
        "<div class='ai-card'>"
        f"<div class='ai-tag'>{icon('spark', 16)}<span>AI</span></div>"
        f"<div class='ai-text'>{esc(headline)}</div></div>"
    )


def ai_items_html(items, kind="obs"):
    """items: list of dicts {title, body, note}. Small cards, one per point."""
    cards = []
    for item in items:
        title = f"<div class='ai-item-title'>{esc(item['title'])}</div>" if item.get("title") else ""
        body = f"<div class='ai-item-body'>{esc(item['body'])}</div>" if item.get("body") else ""
        note = f"<div class='ai-item-note'>{esc(item['note'])}</div>" if item.get("note") else ""
        cards.append(f"<div class='ai-item {kind}'><div class='ai-dot'></div><div>{title}{body}{note}</div></div>")
    return "<div class='ai-items'>" + "".join(cards) + "</div>"


def render_ai_answer(headline):
    st.markdown(ai_answer_html(headline), unsafe_allow_html=True)


def render_ai_items(items, kind="obs"):
    st.markdown(ai_items_html(items, kind), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Dashboard cards: one white card per chart, in a two-column grid (full width on phones)
# ---------------------------------------------------------------------------

PALETTE = ["#2f6feb", "#c2410c", "#0f766e", "#7c3aed", "#b45309", "#667085"]


def dcard_html(title, body, wide=False, hint=""):
    foot = f"<div class='dsub'>{icon('info', 15)}<span>{esc(hint)}</span></div>" if hint else ""
    return f"<div class='dcard{' wide' if wide else ''}'><div class='dtitle'>{esc(title)}</div>{body}{foot}</div>"


def grid_html(cards):
    return "<div class='dgrid'>" + "".join(cards) + "</div>"


def render_grid(cards):
    if cards:
        st.markdown(grid_html(cards), unsafe_allow_html=True)


def ranking_body_html(rows):
    """rows: list of (name, small text under the name, amount text). Numbered, the first one in solid colour."""
    out = []
    for index, (name, sub, amount) in enumerate(rows, start=1):
        small = f"<div class='rk-sub'>{esc(sub)}</div>" if sub else ""
        out.append(
            f"<div class='rk-row{' first' if index == 1 else ''}'><div class='rk-n'>{index}</div>"
            f"<div class='rk-main'><div class='rk-name'>{esc(name)}</div>{small}</div>"
            f"<div class='rk-amt'>{esc(amount)}</div></div>"
        )
    return "".join(out)


def share_bars_body_html(rows):
    """rows: list of (name, amount text, percent number 0-100). Name left, amount and percent right, bar below."""
    out = []
    for name, amount, pct in rows:
        width = max(0.0, min(100.0, float(pct)))
        out.append(
            f"<div class='sb-row'><div class='sb-top'><span>{esc(name)}</span><b>{esc(amount)}</b></div>"
            f"<div class='sb-track'><div class='sb-fill' style='width:{width:.1f}%'></div></div></div>"
        )
    return "".join(out)


def split_body_html(rows):
    """rows: list of (name, amount text, percent number). One long bar split in coloured parts, then a legend."""
    segments, legend = [], []
    for index, (name, amount, pct) in enumerate(rows):
        colour = PALETTE[index % len(PALETTE)]
        if pct >= 1:
            label = f"{esc(name)} {pct:.0f}%" if pct >= 14 else ""
            segments.append(f"<div class='sp-seg' style='width:{pct:.2f}%;background:{colour}' title='{esc(name)} {pct:.1f}%'>{label}</div>")
        legend.append(f"<div class='sp-row'><span><i style='background:{colour}'></i>{esc(name)}</span><b>{esc(amount)}</b></div>")
    return f"<div class='sp-bar'>{''.join(segments)}</div>{''.join(legend)}"


def _nice_top(value):
    if value <= 0:
        return 1.0
    power = 10 ** (len(str(int(value))) - 1) if value >= 1 else 1
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * power:
            return step * power
    return 10 * power


def line_svg_html(points, fmt, tips=None, size=(1000, 300)):
    """A line chart drawn as SVG. Hover over a point (no script needed) and a small box tells about it.
    points: list of (label, value); tips: optional list of extra lines per point."""
    W, H = size
    pad_l, pad_r, pad_t, pad_b = 78, 22, 16, 36
    points = [(str(label), float(value)) for label, value in points]
    if len(points) < 2:
        return ""
    top = _nice_top(max(max(v for _, v in points), 0))
    low = min(min(v for _, v in points), 0)
    span = (top - low) or 1
    iw, ih = W - pad_l - pad_r, H - pad_t - pad_b

    def x_of(i):
        return pad_l + iw * i / (len(points) - 1)

    def y_of(v):
        return pad_t + ih * (1 - (v - low) / span)

    grid = "".join(
        f"<line x1='{pad_l}' x2='{W - pad_r}' y1='{y_of(low + span * k / 4):.1f}' y2='{y_of(low + span * k / 4):.1f}' stroke='#eef0f4'/>"
        f"<text x='{pad_l - 10}' y='{y_of(low + span * k / 4) + 5:.1f}' text-anchor='end' font-size='13' fill='#667085'>{esc(fmt(low + span * k / 4))}</text>"
        for k in range(5)
    )
    path = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, (_, v) in enumerate(points))
    base = y_of(max(low, 0))
    area = f"{x_of(0):.1f},{base:.1f} {path} {x_of(len(points) - 1):.1f},{base:.1f}"
    ticks = sorted({0, len(points) // 4, len(points) // 2, (3 * len(points)) // 4, len(points) - 1})
    labels = "".join(
        f"<text x='{x_of(i):.1f}' y='{H - 10}' text-anchor='{'start' if i == 0 else 'end' if i == len(points) - 1 else 'middle'}'"
        f" font-size='13' fill='#667085'>{esc(points[i][0])}</text>" for i in ticks)
    step = iw / (len(points) - 1)
    hover = []
    for i, (label, value) in enumerate(points):
        x, y = x_of(i), y_of(value)
        lines = [label, fmt(value)] + list((tips[i] if tips else []) or [])
        box_w = max(len(line) for line in lines) * 7.6 + 26
        box_h = 14 + 22 * len(lines)
        bx = x + 14 if x + 14 + box_w < W - 4 else x - 14 - box_w
        by = max(pad_t + 2, min(y - box_h / 2, H - pad_b - box_h))
        text = "".join(
            f"<text x='{bx + 13:.1f}' y='{by + 24 + 22 * n:.1f}' font-size='13' "
            f"fill='{'#fff' if n < 2 else '#d0d5dd'}' font-weight='{700 if n < 2 else 400}'>{esc(line)}</text>"
            for n, line in enumerate(lines))
        hover.append(
            "<g class='lp'>"
            f"<rect x='{x - step / 2:.1f}' y='{pad_t}' width='{step:.1f}' height='{ih}' fill='transparent'/>"
            f"<g class='lp-on'><line x1='{x:.1f}' x2='{x:.1f}' y1='{pad_t}' y2='{pad_t + ih}' stroke='#9bb8f5' stroke-dasharray='4 4'/>"
            f"<circle cx='{x:.1f}' cy='{y:.1f}' r='6' fill='#2f6feb' stroke='#fff' stroke-width='2.5'/>"
            f"<rect x='{bx:.1f}' y='{by:.1f}' width='{box_w:.1f}' height='{box_h}' rx='10' fill='#101828'/>{text}</g></g>")
    dots = "".join(
        f"<circle cx='{x_of(i):.1f}' cy='{y_of(v):.1f}' r='3.5' fill='#fff' stroke='#2f6feb' stroke-width='2.2'/>"
        for i, (_, v) in enumerate(points)) if len(points) <= 40 else ""
    return (
        f"<svg class='linechart' viewBox='0 0 {W} {H}' width='100%' role='img'>"
        "<defs><linearGradient id='lgfill' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2f6feb' stop-opacity='.22'/>"
        "<stop offset='1' stop-color='#2f6feb' stop-opacity='0'/></linearGradient></defs>"
        f"{grid}<polygon points='{area}' fill='url(#lgfill)'/>"
        f"<polyline points='{path}' fill='none' stroke='#2f6feb' stroke-width='3.5' stroke-linejoin='round' stroke-linecap='round'/>"
        f"{dots}{labels}{''.join(hover)}</svg>"
    )


def alert_grid_html(alerts):
    """alerts: list of dicts {severity, title, detail}. Two columns on a wide screen."""
    return "<div class='agrid'>" + "".join(alert_card_html(a["severity"], a["title"], a.get("detail", "")) for a in alerts) + "</div>"


def render_alert_grid(alerts):
    if alerts:
        st.markdown(alert_grid_html(alerts), unsafe_allow_html=True)
