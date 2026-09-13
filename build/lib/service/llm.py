"""Minimal OpenAI-compatible chat adapter for local or user-managed inference servers."""

from __future__ import annotations

import json
import os
import urllib.request


class ChatClient:
    def __init__(self, base_url: str, model: str, timeout: int = 45):
        if not base_url.startswith(("http://127.0.0.1:", "http://localhost:", "https://")):
            raise ValueError("Use a local endpoint or HTTPS")
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.timeout = timeout

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps({"model": self.model, "temperature": 0,
                              "messages": [{"role": "system", "content": system},
                                           {"role": "user", "content": user}]}).encode()
        headers = {"Content-Type": "application/json"}
        if os.getenv("LLM_API_KEY"):
            headers["Authorization"] = "Bearer " + os.environ["LLM_API_KEY"]
        request = urllib.request.Request(self.endpoint, payload, headers, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            result = json.load(response)
        return result["choices"][0]["message"]["content"]
