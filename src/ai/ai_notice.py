"""The message shown where the AI explanation button would be, when no local AI is available."""

import streamlit as st

from src.ai import hosted_guard


def render_ai_unavailable(status):
    """Explain, in plain words, why there is no AI button and how to get one."""
    model = status.get("model", "qwen3:1.7b")

    if status.get("reason") == "model_missing":
        st.info(
            "The AI program (Ollama) is running on this computer, but the model "
            f"**{model}** is not installed yet. Install it with this command, then reload the page:"
        )
        st.code(f"ollama pull {model}", language="bash")
        return

    st.info(
        "**AI explanations run on your own computer**, so they are switched off on this website. "
        "Everything else on this page works without them: the summary, the alerts, the charts and the reports."
    )
    with st.expander("How to turn on AI explanations (free)"):
        st.markdown(
            "1. Install **Ollama** from ollama.com (free, runs on your computer).\n"
            "2. Download the model once:\n"
        )
        st.code(f"ollama pull {model}", language="bash")
        st.markdown(
            "3. Download this project and start it on your computer:\n"
        )
        st.code("python -m streamlit run app.py", language="bash")
        st.caption(
            "Your files then stay on your computer, and the AI button appears automatically."
        )


def ai_gate(status, key):
    """Before the AI button: when the online AI is used, ask for consent and show what is left.

    Returns True when the button may be shown. With the local AI (Ollama) it always returns True.
    """
    if status.get("provider") != "groq":
        return True

    st.info(
        "**AI explanations on this website use a free online AI service (Groq).** "
        "If you continue, a summary is sent there: the totals, the names of groups such as products "
        "or regions, the alerts, and anything you type in the boxes above. "
        "Your file itself is not sent. Do not type personal data."
    )
    left = hosted_guard.remaining()
    if left["daily_left"] <= 0:
        st.warning("The free AI allowance for today has been used up. It starts again tomorrow.")
        return False
    if left["session_left"] <= 0:
        st.warning("You have used all the AI requests for this visit. Reload the page later to try again.")
        return False

    agreed = st.checkbox(
        "I understand, and I agree to send this summary to the online AI",
        key=f"ai_consent_{key}",
    )
    st.caption(f"AI requests left in this visit: {left['session_left']}")
    return bool(agreed)
