"""Streamlit pieces for privacy: the notice and the personal-data warning."""

import streamlit as st

from src.security import upload_guard as ug
from src.i18n import t


def _md(text):
    return str(text).replace("$", "\\$")


def render_privacy_note():
    st.caption(
        t("Free test version: your file is processed in memory during your visit and this app does not "
          "save it. Please do not upload personal data or files you are not allowed to share.")
    )


def apply_personal_data_choice(df, key):
    """Warn about columns that look like personal data and, by default, remove them.

    Returns (table, list_of_removed_columns).
    """
    found = ug.find_personal_columns(df)
    if not found:
        return df, []

    listing = "; ".join(f"**{_md(column)}** ({t(reason)})" for column, reason in found.items())
    st.warning(
        t("Some columns look like personal data: {listing}. "
          "You do not need them for sales analysis, and keeping personal data out is safer.", listing=listing)
    )
    remove = st.checkbox(t("Remove these columns before analysis (recommended)"), value=True, key=key)
    if remove:
        return df.drop(columns=list(found)), list(found)
    return df, []
