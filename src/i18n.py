"""Translations: English text is the key, Spanish comes from src/locales/es.py.

    t("Total {label}", label="revenue")   ->  "Total ingresos" when the language is Spanish

A text that has no Spanish entry is simply shown in English, so nothing breaks.
Pure Python modules can use it too: the language is read from the visitor's session when
Streamlit is running, and is English otherwise.
"""

LANGUAGES = {"en": "English", "es": "Español"}
DEFAULT_LANGUAGE = "en"
_fallback = {"lang": DEFAULT_LANGUAGE}   # used outside Streamlit (tests, scripts)


def _catalog():
    from src.locales.es import ES

    return ES


def set_language(code):
    code = code if code in LANGUAGES else DEFAULT_LANGUAGE
    _fallback["lang"] = code
    try:
        import streamlit as st

        st.session_state["lang"] = code
    except Exception:
        pass


def get_language():
    try:
        import streamlit as st

        code = st.session_state.get("lang")
        if code in LANGUAGES:
            return code
    except Exception:
        pass
    return _fallback["lang"]


def is_spanish():
    return get_language() == "es"


def t(text, **values):
    """Translate `text` (English) into the current language and fill in {placeholders}."""
    out = _catalog().get(text, text) if get_language() == "es" else text
    return out.format(**values) if values else out


def language_instruction():
    """A line for the AI prompt asking it to answer in the visitor's language ('' for English)."""
    if get_language() != "es":
        return ""
    return (
        "LANGUAGE: Write every text value of the JSON in Spanish (neutral Latin American Spanish), "
        "in short, plain sentences. Keep the JSON keys and the fact IDs exactly as given. "
        "Copy numbers, product names and other names exactly as they appear in the facts."
    )


def detect_browser_language():
    """'es' when the visitor's browser prefers Spanish, otherwise 'en'."""
    try:
        import streamlit as st

        header = st.context.headers.get("Accept-Language", "") or ""
        first = header.split(",")[0].strip().lower()
        return "es" if first.startswith("es") else "en"
    except Exception:
        return DEFAULT_LANGUAGE
