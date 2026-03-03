"""Multi-query decomposition for complex questions."""

import json

from openai import OpenAI

from contractiq.config import get_settings


DECOMPOSE_PROMPT = """\
You are a query decomposition assistant for a contract analysis system.
Given a complex user question, break it down into 3-5 simpler sub-queries that together cover all aspects of the original question.

Each sub-query should:
- Be a self-contained search query
- Target a specific piece of information from supplier contracts
- Use precise contract terminology

Return a JSON array of strings.

Example:
User: "Compare the payment terms and liability limits across all our technology suppliers"
Output: ["What are the payment terms for technology supplier contracts?", "What are the payment due dates and late payment penalties?", "What is the limitation of liability for technology suppliers?", "What are the aggregate liability caps across technology contracts?"]

User question: {query}

Output:"""


class MultiQueryDecomposer:
    """Decomposes complex queries into multiple sub-queries."""

    def __init__(self):
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model

    def decompose(self, query: str) -> list[str]:
        """Decompose a complex query into sub-queries.

        Args:
            query: Complex user question.

        Returns:
            List of 3-5 sub-queries.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": DECOMPOSE_PROMPT.format(query=query)},
            ],
            temperature=0.0,
            max_tokens=500,
        )

        content = response.choices[0].message.content.strip()

        try:
            sub_queries = json.loads(content)
            if isinstance(sub_queries, list):
                return sub_queries[:5]
        except json.JSONDecodeError:
            pass

        # Fallback: return original query
        return [query]

    def is_complex(self, query: str) -> bool:
        """Heuristic check if a query should be decomposed."""
        indicators = [
            " and " in query.lower(),
            " compare " in query.lower(),
            " across " in query.lower(),
            " between " in query.lower(),
            " versus " in query.lower(),
            query.count("?") > 1,
            len(query.split()) > 20,
        ]
        return sum(indicators) >= 2
