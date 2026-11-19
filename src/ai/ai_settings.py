"""Read a setting from an environment variable or from Streamlit Secrets (never from code)."""

import os


def get_setting(name, default=""):
    value = os.environ.get(name)
    if value:
        return str(value).strip()
    try:
        import streamlit as st

        value = st.secrets.get(name, "")
        return str(value).strip() if value else default
    except Exception:
        return default


def get_int_setting(name, default):
    try:
        return max(0, int(get_setting(name, str(default))))
    except (TypeError, ValueError):
        return default
