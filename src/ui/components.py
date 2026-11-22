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
        cards.append(
            "<div class='kpi'>"
            f"<div class='kpi-icon'>{icon(item.get('icon', 'chart'), 20)}</div>"
            f"<div class='kpi-label'>{esc(item['label'])}</div>"
            f"<div class='kpi-value'>{esc(item['value'])}</div>"
            f"{chip}</div>"
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
