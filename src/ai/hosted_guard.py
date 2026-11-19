"""Limits for the shared online AI, so the free quota lasts and one visitor cannot use it all.

Three limits (all counted per AI request sent to the online service):
- a daily cap for the whole app,
- a cap for each visitor's session,
- a short burst limit, so the service's per-minute limit is not hit.

The daily counter lives in the server's memory. The free host has no database, so it starts
again from zero if the app restarts. The online service's own limit still protects you then.
"""

import threading
import time
from collections import deque
from datetime import datetime, timezone

from src.ai.ai_settings import get_int_setting

DEFAULT_DAILY_CAP = 45     # about 20-45 reports, depending on retries
DEFAULT_SESSION_CAP = 4
BURST_CALLS = 2
BURST_SECONDS = 60
SESSION_KEY = "_hosted_ai_used"


class AiLimitReached(RuntimeError):
    """A limit was reached. The message is written to be shown to the visitor."""


_lock = threading.Lock()
_day = {"date": None, "count": 0}
_recent = deque()


def _today():
    return datetime.now(timezone.utc).date().isoformat()


def _session_state():
    try:
        import streamlit as st

        return st.session_state
    except Exception:
        return {}


def daily_cap():
    return get_int_setting("GROQ_DAILY_CAP", DEFAULT_DAILY_CAP)


def session_cap():
    return get_int_setting("GROQ_SESSION_CAP", DEFAULT_SESSION_CAP)


def remaining():
    """What is left right now: {"daily_left", "session_left", "ok"}."""
    with _lock:
        if _day["date"] != _today():
            _day.update(date=_today(), count=0)
        daily_left = max(0, daily_cap() - _day["count"])
    session_left = max(0, session_cap() - int(_session_state().get(SESSION_KEY, 0)))
    return {"daily_left": daily_left, "session_left": session_left, "ok": daily_left > 0 and session_left > 0}


def reserve():
    """Count one request, or raise AiLimitReached. Call release() if it never reached the service."""
    state = _session_state()
    with _lock:
        today = _today()
        if _day["date"] != today:
            _day.update(date=today, count=0)

        if _day["count"] >= daily_cap():
            raise AiLimitReached(
                "The free AI allowance for today has been used up. It starts again tomorrow. "
                "Everything else on this page still works."
            )
        if int(state.get(SESSION_KEY, 0)) >= session_cap():
            raise AiLimitReached(
                "You have used all the AI requests for this visit. Reload the page later to try again."
            )

        now = time.monotonic()
        while _recent and now - _recent[0] > BURST_SECONDS:
            _recent.popleft()
        if len(_recent) >= BURST_CALLS:
            raise AiLimitReached("The AI is busy right now. Please try again in a minute.")

        _recent.append(now)
        _day["count"] += 1
        state[SESSION_KEY] = int(state.get(SESSION_KEY, 0)) + 1


def release():
    """Give back one request that never reached the service (for example a network failure)."""
    state = _session_state()
    with _lock:
        if _day["count"] > 0:
            _day["count"] -= 1
        if _recent:
            _recent.pop()
        state[SESSION_KEY] = max(0, int(state.get(SESSION_KEY, 0)) - 1)


def reset_for_tests():
    with _lock:
        _day.update(date=None, count=0)
        _recent.clear()
