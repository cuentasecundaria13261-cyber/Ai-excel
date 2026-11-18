import json
import os
import socket
import time
import urllib.error
import urllib.request

# The AI runs on the computer where Ollama is installed. These can be changed
# without editing code by setting environment variables before starting the app:
#   OLLAMA_URL    (default http://localhost:11434)
#   OLLAMA_MODEL  (default qwen3:1.7b, for example qwen3:4b for better answers)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:1.7b")

CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

_STATUS_TTL_SECONDS = 15
_status_cache = {"time": 0.0, "value": None}


def ai_status(timeout=1.5, use_cache=True):
    """Check whether the local AI can be used. Never raises.

    Returns {"available": bool, "reason": "ok" | "not_running" | "model_missing",
             "model": str}.
    """
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
