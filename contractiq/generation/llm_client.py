"""OpenAI LLM client with retry logic and token tracking."""

import tiktoken
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from contractiq.config import get_settings


class LLMClient:
    """OpenAI chat completion client with retry and token tracking."""

    def __init__(self):
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        try:
            self._encoding = tiktoken.encoding_for_model(self._model)
        except KeyError:
            self._encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self._encoding.encode(text))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request.

        Args:
            system_prompt: System message.
            user_prompt: User message.
            temperature: Override temperature.
            max_tokens: Override max tokens.

        Returns:
            Assistant response text.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature if temperature is not None else self._temperature,
            max_tokens=max_tokens or self._max_tokens,
        )

        usage = response.usage
        if usage:
            self._total_prompt_tokens += usage.prompt_tokens
            self._total_completion_tokens += usage.completion_tokens

        return response.choices[0].message.content.strip()

    @property
    def total_tokens(self) -> dict[str, int]:
        return {
            "prompt": self._total_prompt_tokens,
            "completion": self._total_completion_tokens,
            "total": self._total_prompt_tokens + self._total_completion_tokens,
        }
