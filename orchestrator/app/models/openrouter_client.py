import os

import httpx


class OpenRouterClient:
    """OpenAI-compatible OpenRouter client.

    The API key is read only from OPENROUTER_API_KEY.
    The default model is openrouter/free so the hosted model can change
    without changing TonyAI application code.
    """

    def __init__(self):
        self.base_url = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        ).rstrip("/")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.default_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        self.app_url = os.getenv("OPENROUTER_APP_URL", "")
        self.app_name = os.getenv("OPENROUTER_APP_NAME", "TonyAI")
        self.timeout_seconds = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "120"))

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured. "
                "Set it before using AI_PROVIDER=openrouter."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.app_url:
            headers["HTTP-Referer"] = self.app_url
        if self.app_name:
            headers["X-Title"] = self.app_name

        return headers

    async def chat(
        self,
        model: str,
        messages: list[dict],
        keep_alive=0,
        temperature=0.2,
    ) -> str:
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
        }

        timeout = httpx.Timeout(
            self.timeout_seconds,
            connect=15.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            choices = data.get("choices") or []
            if not choices:
                raise RuntimeError("OpenRouter returned no choices.")

            return choices[0].get("message", {}).get("content", "")

    async def health(self) -> bool:
        if not self.api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._headers(),
                )
                return response.is_success
        except Exception:
            return False
