
import json
import urllib.request
import urllib.error
import urllib.parse
import time

import keyring



def send_request(url, headers, payload):

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:

            retryable_errors = {
                429, 500, 502, 503, 504
            }

            details = error.read().decode(
                "utf-8",
                errors="replace"
            )

            if error.code not in retryable_errors:
                raise RuntimeError(
                    f"AI provider returned HTTP "
                    f"{error.code}: {details}"
                )

            if attempt == max_attempts - 1:
                raise RuntimeError(
                    f"AI provider unavailable after "
                    f"{max_attempts} attempts. "
                    f"HTTP {error.code}: {details}"
                )

            retry_after = error.headers.get("Retry-After")

            try:
                wait_time = min(float(retry_after), 30)
            except (TypeError, ValueError):
                wait_time = 2 ** (attempt + 1)

            print(
                f"\nAI provider temporarily unavailable. "
                f"Retrying in {wait_time:g} seconds... "
                f"({attempt + 1}/{max_attempts - 1})"
            )

            time.sleep(wait_time)



def generate_text(config, prompt):
    provider = config.get("ai_provider")
    model = config.get("ai_model")
    base_url = config.get("ai_base_url", "").rstrip("/")

    if not provider or not model:
        raise RuntimeError("No AI model is configured.")

    api_key = None

    if provider != "ollama":
        api_key = keyring.get_password("anton", provider)

        if not api_key:
            raise RuntimeError("AI credentials were not found in Keychain.")

    if provider == "ollama":
        url = f"{base_url}/api/chat"

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        headers = {"Content-Type": "application/json"}

        response = send_request(url, headers, payload)

        return response["message"]["content"]

    elif provider == "openai":
        url = f"{base_url}/v1/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = send_request(url, headers, payload)

        return extract_gemini_response(response)

    elif provider == "gemini":
        url = (
            f"{base_url}/v1beta/models/"
            f"{urllib.parse.quote(model, safe='')}:generateContent?"
            f"{urllib.parse.urlencode({'key': api_key})}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}

        response = send_request(url, headers, payload)

        return response["candidates"][0]["content"]["parts"][0]["text"]

    elif provider == "anthropic":
        url = f"{base_url}/v1/messages"

        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }

        response = send_request(url, headers, payload)

        return "\n".join(
            block["text"]
            for block in response["content"]
            if block["type"] == "text"
        )

    else:
        raise RuntimeError(f"Unsupported AI provider: {provider}")
def extract_gemini_response(response):

    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            "Gemini returned an unexpected response format."
        )