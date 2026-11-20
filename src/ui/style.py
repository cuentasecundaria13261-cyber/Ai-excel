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
</style>
"""


def apply_style():
    """Call once, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)


def steps_html(active):
    """The strip "1 Add your file - 2 Read the results - 3 Save or share". `active` is 0, 1 or 2."""
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
