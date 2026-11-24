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

/* language switch: a small pill with two options */
.st-key-lang [role="radiogroup"] { gap:4px !important; background:#e9edf3; padding:4px; border-radius:12px; width:100%; }
.st-key-lang label { flex:1; justify-content:center; margin:0 !important; padding:.35rem .5rem; border-radius:9px; cursor:pointer; }
.st-key-lang label > div:first-child { display:none !important; }
.st-key-lang label p { font-size:.9rem; font-weight:600; color:#475467; text-align:center; }
.st-key-lang label:has(input:checked) { background:#fff; box-shadow:0 1px 3px rgba(16,24,40,.15); }
.st-key-lang label:has(input:checked) p { color:var(--accent); }

/* the button that slides the side panel in and out: always visible, easy to hit */
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"], [data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] button { visibility:visible !important; opacity:1 !important; }
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:flex !important; top:.7rem; left:.7rem; z-index:1000; }
[data-testid="stSidebarCollapsedControl"] button, [data-testid="collapsedControl"] button, [data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] button {
  background:#fff !important; border:1px solid var(--line) !important; border-radius:12px !important; color:var(--accent) !important;
  width:42px; height:42px; box-shadow:0 2px 8px rgba(16,24,40,.12); transition:border-color .15s, transform .15s; }
[data-testid="stSidebarCollapsedControl"] button:hover, [data-testid="collapsedControl"] button:hover,
[data-testid="stExpandSidebarButton"]:hover, [data-testid="stSidebarCollapseButton"] button:hover { border-color:var(--accent) !important; transform:scale(1.05); }
[data-testid="stSidebar"] { transition:transform .3s ease; }

/* page choice: big, clear buttons instead of round radio dots */
.st-key-main_navigation [role="radiogroup"] { gap:8px !important; }
.st-key-main_navigation label { width:100%; margin:0 !important; padding:.8rem 1rem; background:#fff; border:1px solid var(--line);
  border-radius:14px; cursor:pointer; transition:border-color .15s, background .15s; }
.st-key-main_navigation label > div:first-child { display:none !important; }
.st-key-main_navigation label { flex-wrap:wrap; align-items:center; }
.st-key-main_navigation label p { font-size:1rem; font-weight:600; color:#344054; display:flex; align-items:center; gap:.5rem; }
.st-key-main_navigation label p span[data-testid="stIconMaterial"], .st-key-main_navigation label p [class*="Icon"] { font-size:1.45rem; color:var(--accent); }
.st-key-main_navigation label [data-testid="stCaptionContainer"], .st-key-main_navigation label small { flex-basis:100%; margin-top:.15rem; color:var(--muted); font-size:.82rem; font-weight:400; }
.st-key-main_navigation label:hover { border-color:#9bb8f5; }
.st-key-main_navigation label:has(input:checked) { background:#eaf1fe; border-color:var(--accent); box-shadow:0 0 0 1px var(--accent) inset; }
.st-key-main_navigation label:has(input:checked) p { color:var(--accent); }

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

/* bar chart */
.bars { background:#fff; border:1px solid var(--line); border-radius:16px; padding:18px 20px; margin:.4rem 0 1rem; box-shadow:0 1px 2px rgba(16,24,40,.04); }
.bar-title { font-weight:650; font-size:1.02rem; margin-bottom:.8rem; }
.bar-row { display:grid; grid-template-columns:minmax(80px,28%) 1fr auto; gap:12px; align-items:center; margin:.5rem 0; }
.bar-name { font-size:.92rem; color:#344054; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.bar-track { background:#eef2fb; border-radius:999px; height:14px; overflow:hidden; }
.bar-fill { background:var(--accent); height:100%; border-radius:999px; min-width:4px; }
.bar-value { font-size:.9rem; font-weight:600; color:#1f2430; min-width:3.5rem; text-align:right; }
.bar-hint { display:flex; gap:8px; align-items:center; color:var(--muted); font-size:.85rem; margin-top:.9rem; }
/* AI answer */
.ai-card { background:linear-gradient(135deg,#f3f7ff 0%,#fff 70%); border:1px solid #d6e3fd; border-radius:18px; padding:20px 22px; margin:.4rem 0 1rem; }
.ai-tag { display:inline-flex; gap:6px; align-items:center; background:#eaf1fe; color:var(--accent); font-weight:700; font-size:.78rem;
          letter-spacing:.04em; padding:3px 10px; border-radius:999px; margin-bottom:.7rem; }
.ai-text { font-size:1.12rem; line-height:1.55; font-weight:550; }
.ai-items { display:grid; gap:10px; margin:.3rem 0 1rem; }
.ai-item { display:flex; gap:12px; background:#fff; border:1px solid var(--line); border-radius:14px; padding:14px 16px; }
.ai-dot { width:10px; height:10px; border-radius:50%; background:var(--accent); margin-top:.45rem; flex:none; }
.ai-item.rec .ai-dot { background:#12b76a; }
.ai-item-title { font-weight:650; margin-bottom:.15rem; }
.ai-item-body { color:#344054; line-height:1.5; }
.ai-item-note { color:var(--muted); font-size:.85rem; margin-top:.35rem; }
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
