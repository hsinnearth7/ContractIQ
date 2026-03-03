"""Extract structured contract metadata using GPT-4o."""

from openai import OpenAI

from contractiq.config import get_settings
from contractiq.parsing.models import ContractMetadata


EXTRACTION_PROMPT = """\
You are a contract analysis expert. Extract structured metadata from the following contract text.
Return a JSON object with these fields:
- supplier_name: The supplier/vendor company name
- buyer_name: The buyer/client company name
- contract_type: One of "MSA", "PO", "NDA", "SLA", or "OTHER"
- agreement_number: The contract/agreement ID number
- effective_date: The contract start/effective date
- expiration_date: The contract end date (if stated)
- contract_value: Total contract value/amount (as string with currency symbol)
- currency: Currency code (default USD)
- governing_law: Jurisdiction or governing law state/country
- key_terms: List of 3-5 key terms or highlights from the contract

Analyze this contract text:

{text}
"""


def extract_metadata(text: str, max_chars: int = 6000) -> ContractMetadata:
    """Extract metadata from contract text using GPT-4o structured output.

    Args:
        text: Raw contract text (will be truncated to max_chars).
        max_chars: Maximum characters to send to the LLM.

    Returns:
        ContractMetadata with extracted fields.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)

    # Use beginning + end of document for best coverage
    if len(text) > max_chars:
        half = max_chars // 2
        truncated = text[:half] + "\n\n[...]\n\n" + text[-half:]
    else:
        truncated = text

    try:
        response = client.beta.chat.completions.parse(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "Extract contract metadata as JSON."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(text=truncated)},
            ],
            response_format=ContractMetadata,
            temperature=0.0,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        # Return empty metadata on failure rather than crashing the pipeline
        print(f"  Warning: metadata extraction failed: {e}")
        return ContractMetadata()
