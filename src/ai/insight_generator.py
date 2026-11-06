import json

from src.ai.prompt_builder import (
    build_business_prompt,
    build_fact_catalog,
)
from src.ai.ai_service import generate_response
from src.ai.insight_validator import validate_insight_payload


def generate_business_insights(analytics):
    """
    Generate structured AI interpretations and validate their structure
    and evidence references against calculated analytics.
    """

    prompt = build_business_prompt(analytics)
    response = generate_response(prompt)

    try:
        payload = json.loads(response)

    except (TypeError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "Ollama did not return valid JSON. "
            "Try generating the insights again."
        ) from error

    fact_catalog = build_fact_catalog(analytics)

    known_fact_ids = {
        fact["id"] for fact in fact_catalog
    }

    issues = validate_insight_payload(
        payload,
        known_fact_ids
    )

    return {
        "insights": payload,
        "fact_catalog": fact_catalog,
        "validation_issues": issues,
        "structure_valid": len(issues) == 0,
    }