"""The message shown where the AI explanation button would be, when no local AI is available."""

import streamlit as st


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
