"""A small feedback form for the sidebar.

Where the answers go (the owner chooses, all optional and free):
1. FEEDBACK_WEBHOOK_URL (https): each answer is sent there as JSON. A free Google Apps Script
   or Formspree endpoint works. Set it in Streamlit Cloud under Settings > Secrets, or as an
   environment variable.
2. Otherwise the answer is appended to feedback_data/feedback.jsonl on the server. On the free
   Streamlit host that file is erased when the app restarts, so use option 1 for the public site.
3. FEEDBACK_ISSUES_URL (optional): shows a "report on GitHub" link too.
4. FEEDBACK_EMAIL (optional): shows "you can also write to us" with a mail link. It is read from
   the secrets, so the address is not written in the public code.

Only what the visitor types here is saved. Their uploaded data is never included.
"""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

import streamlit as st

from src.i18n import t
from src.security.upload_guard import neutralize_cell, sanitize_label

FEEDBACK_DIR = os.environ.get("FEEDBACK_DIR", "feedback_data")
MAX_MESSAGE = 1000
MAX_CONTACT = 120
MIN_SECONDS_BETWEEN = 30
MOODS = ["Very useful", "Useful", "So-so", "Not useful"]
TOPICS = ["General", "Something is broken", "An idea", "Confusing"]


def _setting(name):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, "") or "")
    except Exception:
        return ""


_EMAIL_OK = __import__("re").compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def owner_email():
    """The owner's address from the settings, or '' when it is missing or not an email."""
    value = _setting("FEEDBACK_EMAIL").strip()
    return value if _EMAIL_OK.match(value) and len(value) <= 120 else ""


def clean_entry(mood, topic, message, contact, page):
    """Turn the form values into a safe record. Returns None when there is nothing to save."""
    message = str(message or "").replace("\r", "\n").strip()
    message = "\n".join(line.strip() for line in message.split("\n") if line.strip())[:MAX_MESSAGE]
    if not message:
        return None
    return {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mood": mood if mood in MOODS else "",
        "topic": topic if topic in TOPICS else "General",
        "page": sanitize_label(page, 40),
        # Spreadsheet-safe: the owner will open these answers in Excel or Sheets.
        "message": neutralize_cell(message),
        "contact": neutralize_cell(sanitize_label(contact, MAX_CONTACT)),
    }


def store_entry(entry):
    """Send or save one record. Returns (ok, where)."""
    url = _setting("FEEDBACK_WEBHOOK_URL")
    if url:
        if not url.lower().startswith("https://"):
            return False, "webhook must use https"
        request = urllib.request.Request(
            url,
            data=json.dumps(entry).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=8):
                return True, "webhook"
        except (urllib.error.URLError, TimeoutError, OSError):
            return False, "could not reach the feedback service"

    try:
        os.makedirs(FEEDBACK_DIR, exist_ok=True)
        with open(os.path.join(FEEDBACK_DIR, "feedback.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True, "file"
    except OSError:
        return False, "could not save"


def render_feedback(page_name=""):
    """The feedback box, meant for the sidebar."""
    with st.expander(t("Send feedback")):
        st.caption(t("Tell us what to improve. No personal data, please."))
        with st.form("feedback_form", clear_on_submit=True):
            mood = st.radio(t("How useful was it?"), MOODS, index=None, key="fb_mood", format_func=t)
            topic = st.selectbox(t("About"), TOPICS, key="fb_topic", format_func=t)
            message = st.text_area(
                t("Your feedback"),
                max_chars=MAX_MESSAGE,
                height=110,
                key="fb_message",
                placeholder=t("What did you try? What would make it better?"),
            )
            contact = st.text_input(
                t("Email, only if you want a reply (optional)"),
                max_chars=MAX_CONTACT,
                key="fb_contact",
            )
            sent = st.form_submit_button(t("Send"))

        if sent:
            last = st.session_state.get("fb_last_sent", 0)
            if time.time() - last < MIN_SECONDS_BETWEEN:
                st.warning(t("Thanks! Please wait a few seconds before sending another one."))
            else:
                entry = clean_entry(mood, topic, message, contact, page_name)
                if entry is None:
                    st.warning(t("Please write a message first."))
                else:
                    ok, _where = store_entry(entry)
                    if ok:
                        st.session_state["fb_last_sent"] = time.time()
                        st.success(t("Thank you! Your feedback was sent."))
                    else:
                        st.error(t("Sorry, your feedback could not be sent. Please try again later."))

        issues_url = _setting("FEEDBACK_ISSUES_URL")
        if issues_url.lower().startswith("https://"):
            st.markdown(f"[{t('Or report it on GitHub')}]({issues_url})")

        email = owner_email()
        if email:
            st.markdown(t("You can also write to us: {email}", email=f"[{email}](mailto:{email})"))
