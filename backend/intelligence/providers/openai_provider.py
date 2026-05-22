import openai

from app.config import settings
from intelligence.providers.base import AbstractLLMProvider


class OpenAIProvider(AbstractLLMProvider):
    def __init__(self):
        self._client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = "gpt-4o"

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def infer(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> dict:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            },
        }

    async def health_check(self) -> bool:
        try:
            await self._client.chat.completions.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False
