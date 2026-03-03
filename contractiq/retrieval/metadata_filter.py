"""Parse query intent to build ChromaDB metadata filters."""

import json

from openai import OpenAI

from contractiq.config import get_settings


FILTER_PROMPT = """\
You are a metadata filter parser for a contract retrieval system.
Given a user query, extract any explicit or implicit metadata filters.

Available metadata fields:
- supplier_name: Supplier/vendor company name (string)
- contract_type: One of "MSA", "PO", "NDA", "SLA", "OTHER"
- agreement_number: Contract ID

Return a JSON object with only the fields that can be clearly inferred from the query.
If no filters can be inferred, return an empty object {{}}.

Examples:
Query: "What are the payment terms for Acme Technologies?"
Output: {{"supplier_name": "Acme Technologies Inc."}}

Query: "Show me all NDA confidentiality periods"
Output: {{"contract_type": "NDA"}}

Query: "What is the SLA uptime guarantee?"
Output: {{"contract_type": "SLA"}}

Query: "Tell me about contract CIQ-MSA-2024-001"
Output: {{"agreement_number": "CIQ-MSA-2024-001"}}

Query: "What are the force majeure clauses?"
Output: {{}}

User query: {query}

Output:"""


class MetadataFilter:
    """Extracts ChromaDB where-clauses from query intent."""

    def __init__(self):
        settings = get_settings()
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model

    def parse(self, query: str) -> dict | None:
        """Parse a query to extract metadata filters.

        Returns:
            ChromaDB where-clause dict, or None if no filters detected.
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": FILTER_PROMPT.format(query=query)},
            ],
            temperature=0.0,
            max_tokens=200,
        )

        content = response.choices[0].message.content.strip()

        try:
            filters = json.loads(content)
            if isinstance(filters, dict) and filters:
                # Build ChromaDB where clause
                if len(filters) == 1:
                    key, val = next(iter(filters.items()))
                    return {key: val}
                else:
                    # Multiple filters → $and
                    conditions = [{k: v} for k, v in filters.items()]
                    return {"$and": conditions}
        except json.JSONDecodeError:
            pass

        return None
