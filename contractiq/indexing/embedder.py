"""OpenAI embedding wrapper with batching and rate limiting."""

import time
from typing import Sequence

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from contractiq.config import get_settings


class OpenAIEmbedder:
    """Wraps OpenAI embedding API with batch processing and rate limiting."""

    def __init__(self, model: str | None = None, dimensions: int | None = None):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.embedding_model
        self.dimensions = dimensions or settings.embedding_dimensions
        self._batch_size = 100  # OpenAI batch limit
        self._total_tokens = 0

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a single batch with retry logic."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            dimensions=self.dimensions,
        )
        self._total_tokens += response.usage.total_tokens
        return [item.embedding for item in response.data]

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed multiple texts with automatic batching.

        Args:
            texts: Texts to embed.

        Returns:
            List of embedding vectors.
        """
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), self._batch_size):
            batch = list(texts[i : i + self._batch_size])
            embeddings = self._embed_batch(batch)
            all_embeddings.extend(embeddings)

            # Rate limit courtesy pause between batches
            if i + self._batch_size < len(texts):
                time.sleep(0.1)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text."""
        return self._embed_batch([text])[0]

    @property
    def total_tokens_used(self) -> int:
        return self._total_tokens
