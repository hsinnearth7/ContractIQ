"""LLM-based query rewriting for improved retrieval."""

from openai import OpenAI

from contractiq.config import get_settings


REWRITE_PROMPT = """\
You are a search query optimizer for a contract document retrieval system.
Given the user's original query, rewrite it to be more effective for both keyword and semantic search against supplier contracts.

Guidelines:
- Expand abbreviations (e.g., "SLA" → "Service Level Agreement")
- Add relevant synonyms and related terms
- Make the query more specific to contract language
- Keep the rewritten query concise (1-2 sentences)
- Do NOT change the intent of the query

Original query: {query}

Rewritten query:"""


class QueryRewriter:
    """Rewrites user queries for better retrieval performance."""

    def __init__(self):
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model

    def rewrite(self, query: str) -> str:
        """Rewrite a query for improved search.

        Args:
            query: Original user query.

        Returns:
            Rewritten query optimized for retrieval.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a query optimization assistant."},
                {"role": "user", "content": REWRITE_PROMPT.format(query=query)},
            ],
            temperature=0.0,
            max_tokens=200,
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten
