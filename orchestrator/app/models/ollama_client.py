import os

import httpx


class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        ).rstrip("/")

    async def chat(
        self,
        model: str,
        messages: list[dict],
        keep_alive=0,
        temperature=0.2,
    ) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": keep_alive,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")

    async def list_models(self):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json()
