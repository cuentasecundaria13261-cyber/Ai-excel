import json
import urllib.request
import urllib.error


def generate_response(prompt):
    """Send the prompt to Ollama and return the JSON-formatted AI response."""
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen3:1.7b",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
            full_response = raw.decode("utf-8")
            # Extract the message content from the Ollama chat response
            # The response format is: {"model": "...", "message": {"role": "assistant", "content": "..."}, ...}
            parsed = json.loads(full_response)
            if "message" in parsed and "content" in parsed["message"]:
                return parsed["message"]["content"]
            else:
                return full_response
    except urllib.error.URLError as e:
        raise RuntimeError(
            "Could not connect to Ollama. "
            "Make sure Ollama is running and the model is loaded."
        ) from e