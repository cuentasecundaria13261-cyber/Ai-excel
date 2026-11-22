"""A calm, minimal look and a clear "what to do now" strip.

Most of the colours come from the theme in .streamlit/config.toml. The CSS below only adds
spacing, rounded corners and hides Streamlit's own menu so visitors see just the app.
If a future Streamlit version renames one of these parts, the page simply keeps its default look.
"""

import html

import streamlit as st

from src.i18n import t

_CSS = """
<style>
:root { --ink:#1f2430; --muted:#6b7280; --line:#e6e8ec; --soft:#f6f7f9; --accent:#2f6feb; }

/* quiet chrome: hide Streamlit's own menu, deploy button and footer */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stDeployButton"] { display:none !important; visibility:hidden; }
header[data-testid="stHeader"] { background:transparent; }

/* one calm column of content */
.block-container { max-width:980px; padding-top:2.2rem; padding-bottom:4rem; }

/* headings: few sizes, clear order */
h1 { font-size:1.9rem !important; font-weight:650 !important; letter-spacing:-0.01em; margin-bottom:.2rem; }
h2 { font-size:1.35rem !important; font-weight:600 !important; margin-top:2.2rem !important; }
h3 { font-size:1.08rem !important; font-weight:600 !important; margin-top:1.4rem !important; }
[data-testid="stCaptionContainer"], .stCaption { color:var(--muted); }

/* cards */
[data-testid="stMetric"] { background:var(--soft); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:12px; }
[data-testid="stAlert"] { border-radius:12px; }

/* the upload area is the main thing on an empty page */
[data-testid="stFileUploaderDropzone"] { border:1.5px dashed #c3c8d1; border-radius:14px; background:var(--soft); padding:1.5rem; }

/* buttons */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  border-radius:10px; padding:.55rem 1.1rem; border:1px solid var(--line); }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--accent); color:var(--accent); }

/* sidebar */
[data-testid="stSidebar"] { background:var(--soft); border-right:1px solid var(--line); }

/* the three-step strip */
.steps { display:flex; flex-wrap:wrap; gap:.4rem .9rem; margin:.6rem 0 1.4rem; font-size:.92rem; color:var(--muted); }
.step { display:flex; align-items:center; gap:.45rem; }
.step .n { width:1.5rem; height:1.5rem; border-radius:50%; border:1.5px solid #c3c8d1;
           display:inline-flex; align-items:center; justify-content:center; font-size:.8rem; }
.step.now { color:var(--ink); font-weight:600; }
.step.now .n { background:var(--accent); border-color:var(--accent); color:#fff; }
.step.done .n { background:#e8f0fe; border-color:#bcd0fb; color:var(--accent); }
.step + .step::before { content:""; width:1.4rem; height:1px; background:var(--line); margin-right:.45rem; }

/* big number cards */
.kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:.4rem 0 1rem; }
.kpi { background:#fff; border:1px solid var(--line); border-radius:16px; padding:16px 18px; box-shadow:0 1px 2px rgba(16,24,40,.04); }
.kpi-icon { width:36px; height:36px; border-radius:10px; background:#eaf1fe; color:var(--accent);
            display:flex; align-items:center; justify-content:center; margin-bottom:10px; }
.kpi-label { color:var(--muted); font-size:.85rem; }
.kpi-value { font-size:1.75rem; font-weight:650; letter-spacing:-0.02em; line-height:1.2; margin:.1rem 0 .4rem; }
.kpi-hint { color:var(--muted); font-size:.78rem; line-height:1.3; margin:0 0 .5rem; }
.chip { display:inline-flex; align-items:center; gap:4px; font-size:.8rem; font-weight:600; padding:2px 9px; border-radius:999px; }
.chip.up { background:#ecfdf3; color:#067647; }
.chip.down { background:#fef3f2; color:#b42318; }
.chip.flat { background:var(--soft); color:var(--muted); }

/* alert cards: colour and icon say how urgent it is */
.alert-card { display:flex; gap:12px; align-items:flex-start; border-radius:14px; padding:14px 16px; margin:.5rem 0; border:1px solid; }
.alert-card.high { background:#fef3f2; border-color:#fecdca; color:#912018; }
.alert-card.medium { background:#fffaeb; border-color:#fedf89; color:#93370d; }
.alert-card.info { background:#eff8ff; border-color:#b2ddff; color:#175cd3; }
.alert-card.ok { background:#ecfdf3; border-color:#abefc6; color:#067647; }
.alert-icon { flex:none; margin-top:1px; }
.alert-title { font-weight:600; }
.alert-detail { font-size:.9rem; opacity:.85; margin-top:2px; }

/* the story: one headline, small lines below */
.story { background:var(--soft); border-radius:16px; padding:18px 20px; margin:.4rem 0 1rem; }
.story-head { font-size:1.15rem; font-weight:600; line-height:1.45; }
.story ul { margin:.6rem 0 0; padding-left:1.1rem; color:#454c5c; }

/* section titles with an icon */
.section { display:flex; align-items:center; gap:10px; font-size:1.3rem; font-weight:600; margin:2.2rem 0 .6rem; }
.section-icon { width:30px; height:30px; border-radius:9px; background:#eaf1fe; color:var(--accent);
                display:inline-flex; align-items:center; justify-content:center; }

/* the empty-state: three big pictures */
.hero-steps { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:1rem 0 1.4rem; }
.hero-step { border:1px solid var(--line); border-radius:16px; padding:18px 12px; text-align:center; background:#fff; }
.hero-step .hi { width:52px; height:52px; border-radius:50%; background:#eaf1fe; color:var(--accent);
                 display:flex; align-items:center; justify-content:center; margin:0 auto 10px; }
.hero-step .ht { font-weight:600; }
.hero-step .hn { color:var(--muted); font-size:.8rem; margin-bottom:2px; }
@media (max-width:640px) {
  .kpis { grid-template-columns:1fr 1fr; }
  .kpi-value { font-size:1.4rem; }
  .hero-steps { gap:8px; }
  .hero-step { padding:12px 6px; }
  .hero-step .hi { width:40px; height:40px; }
  .hero-step .ht { font-size:.8rem; }
}
</style>
"""


def apply_style():
    """Call once, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def hero_steps_html():
    """Three big pictures for the empty page: add, read, share."""
    from src.ui.components import icon

    items = [("upload", t("Add your file")), ("chart", t("Read the results")), ("download", t("Save or share"))]
    cards = "".join(
        f"<div class='hero-step'><div class='hi'>{icon(name, 26)}</div>"
        f"<div class='hn'>{index}</div><div class='ht'>{html.escape(label)}</div></div>"
        for index, (name, label) in enumerate(items, start=1)
    )
    return f"<div class='hero-steps'>{cards}</div>"


def steps_html(active):
    """With nothing uploaded: three big pictures. Afterwards: a small strip. `active` is 0, 1 or 2."""
    if active == 0:
        return hero_steps_html()
    labels = [t("Add your file"), t("Read the results"), t("Save or share")]
    parts = []
    for index, label in enumerate(labels):
        state = "done" if index < active else "now" if index == active else ""
        mark = "&#10003;" if index < active else str(index + 1)
        parts.append(f"<div class='step {state}'><span class='n'>{mark}</span>{html.escape(label)}</div>")
    return "<div class='steps'>" + "".join(parts) + "</div>"


def render_steps(active, slot=None):
    """Show the strip. Pass `slot` (an st.empty()) to be able to change it later on the same page."""
    target = slot if slot is not None else st
    target.markdown(steps_html(active), unsafe_allow_html=True)
