from abc import ABC, abstractmethod


class AbstractLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    async def infer(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> dict:
        """Returns {"content": str, "usage": {"input_tokens": int, "output_tokens": int}}"""
        ...

    @abstractmethod
    async def health_check(self) -> bool: ...
