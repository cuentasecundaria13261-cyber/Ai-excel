import json
import os
import socket
import time
import urllib.error
import urllib.request

from src.ai import hosted_guard
from src.ai.ai_settings import get_setting
from src.i18n import t

# The AI runs on the computer where Ollama is installed. These can be changed
# without editing code by setting environment variables before starting the app:
#   OLLAMA_URL    (default http://localhost:11434)
#   OLLAMA_MODEL  (default qwen3:1.7b, for example qwen3:4b for better answers)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:1.7b")

CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

# Online fallback, used only when Ollama is not available (for example on the public website).
# The key is read from Streamlit Secrets or an environment variable, never from the code:
#   GROQ_API_KEY  (required to turn the online AI on)
#   GROQ_MODEL    (default below)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"
GROQ_TIMEOUT = 60
GROQ_MAX_PROMPT_CHARS = 20_000
GROQ_MAX_OUTPUT_TOKENS = 1500

_STATUS_TTL_SECONDS = 15
_status_cache = {"time": 0.0, "value": None}


def hosted_enabled():
    """True when an online AI key has been set up by the owner."""
    return bool(get_setting("GROQ_API_KEY"))


def hosted_model():
    return get_setting("GROQ_MODEL") or GROQ_DEFAULT_MODEL


def ai_status(timeout=1.5, use_cache=True):
    """Which AI can be used. Never raises.

    Returns {"available": bool, "reason": "ok" | "not_running" | "model_missing",
             "model": str, "provider": "ollama" | "groq" | None}.
    Ollama on this computer is preferred (the data stays here). The online AI is only
    used when Ollama is not available and the owner has set a key.
    """
    local = _ollama_status(timeout=timeout, use_cache=use_cache)
    if local["available"]:
        return {**local, "provider": "ollama"}
    if hosted_enabled():
        return {"available": True, "reason": "ok", "model": hosted_model(), "provider": "groq"}
    return {**local, "provider": None}


def _ollama_status(timeout=1.5, use_cache=True):
    """Check whether the local AI (Ollama) can be used."""
    now = time.monotonic()
    if use_cache and _status_cache["value"] is not None and now - _status_cache["time"] < _STATUS_TTL_SECONDS:
        return _status_cache["value"]

    status = {"available": False, "reason": "not_running", "model": MODEL_NAME}
    try:
        with urllib.request.urlopen(TAGS_URL, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        data = None

    if data is not None:
        installed = {model.get("name", "") for model in data.get("models", []) if isinstance(model, dict)}
        wanted = {MODEL_NAME, f"{MODEL_NAME}:latest"} if ":" not in MODEL_NAME else {MODEL_NAME}
        if installed & wanted:
            status = {"available": True, "reason": "ok", "model": MODEL_NAME}
        else:
            status = {"available": False, "reason": "model_missing", "model": MODEL_NAME}

    _status_cache["time"] = now
    _status_cache["value"] = status
    return status


def generate_response(prompt, timeout=600):
    """Send the prompt to the available AI and return its JSON-formatted answer."""
    if ai_status()["provider"] == "groq":
        return _groq_response(prompt, min(timeout, GROQ_TIMEOUT))
    return _ollama_response(prompt, timeout)


def _groq_response(prompt, timeout=GROQ_TIMEOUT):
    """Ask the online AI. Counts against the daily, session and burst limits."""
    key = get_setting("GROQ_API_KEY")
    model = hosted_model()
    if len(prompt) > GROQ_MAX_PROMPT_CHARS:
        raise RuntimeError(t("This dataset summary is too large for the free online AI. Try filtering the data first."))

    hosted_guard.reserve()   # raises AiLimitReached with a visitor-friendly message

    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "max_completion_tokens": GROQ_MAX_OUTPUT_TOKENS,
    }
    if model.startswith("openai/gpt-oss"):
        body["reasoning_effort"] = "low"   # short answers, fewer tokens used

    def send(payload):
        request = urllib.request.Request(
            GROQ_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}",
                "User-Agent": "ai-excel-dashboard/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    try:
        try:
            data = send(body)
        except urllib.error.HTTPError as error:
            if error.code != 400 or "reasoning_effort" not in body:
                raise
            body.pop("reasoning_effort")      # a model that does not know this option
            data = send(body)
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as error:
        # The service did answer, so the request counts. Never show the key or raw details.
        if error.code in (401, 403):
            raise RuntimeError(t("The online AI rejected the app's key. The owner needs to check it.")) from error
        if error.code == 429:
            raise RuntimeError(t("The free online AI is busy or its limit was reached. Please try again in a minute.")) from error
        raise RuntimeError(t("The online AI returned an error (HTTP {code}). Please try again.", code=error.code)) from error
    except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
        hosted_guard.release()
        raise RuntimeError(t("Could not reach the online AI. Please try again in a moment.")) from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError(t("The online AI sent an answer the app could not read. Please try again.")) from error


def _ollama_response(prompt, timeout=600):
    """Send the prompt to Ollama and return the JSON-formatted AI response."""
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,    # skip Qwen3's <think> reasoning block
        "format": "json",  # make Ollama return valid JSON
        "options": {
            "temperature": 0.2,  # fewer invented details
            "num_ctx": 8192,     # room for the facts + instructions
        },
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        CHAT_URL, data=data, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            full_response = raw.decode("utf-8")
            # The response format is:
            # {"model": "...", "message": {"role": "assistant", "content": "..."}, ...}
            parsed = json.loads(full_response)
            if "message" in parsed and "content" in parsed["message"]:
                return parsed["message"]["content"]
            return full_response
    except urllib.error.HTTPError as e:
        # HTTPError is a subclass of URLError, so it must be caught first.
        detail = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"Ollama returned HTTP {e.code}: {detail} "
            f"(check that the model '{MODEL_NAME}' is installed: ollama list)"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running and the model is loaded."
        ) from e
    except (TimeoutError, socket.timeout) as e:
        raise RuntimeError(
            "Ollama took too long to answer. Try again or use a smaller dataset."
        ) from e
