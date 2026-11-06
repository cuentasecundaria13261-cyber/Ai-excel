import re


def validate_insight_payload(payload, known_fact_ids):
    """Validate the structure and evidence references in an AI response."""

    issues = []

    if not isinstance(payload, dict):
        return ["The AI response must be a JSON object."]

    required_keys = {"summary", "observations", "recommendations"}

    if not required_keys.issubset(set(payload.keys())):
        issues.append(
            "The response must contain summary, "
            "observations, and recommendations."
        )
        return issues

    def validate_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{field_name} must be a non-empty string.")
            return

        if len(value) > 500:
            issues.append(f"{field_name} is too long.")

        if re.search(r"\d", value):
            issues.append(
                f"{field_name} contains numerical digits. "
                "Numerical facts must come from Python."
            )

    def validate_evidence(evidence, field_name):
        if not isinstance(evidence, list) or not evidence:
            issues.append(
                f"{field_name} must contain at least one fact ID."
            )
            return

        for fact_id in evidence:
            if not isinstance(fact_id, str):
                issues.append(
                    f"{field_name} contains an invalid fact ID."
                )
            elif fact_id not in known_fact_ids:
                issues.append(
                    f"{field_name} references unknown fact ID: {fact_id}."
                )

    # Validate summary.
    summary = payload["summary"]

    if not isinstance(summary, dict):
        issues.append("Summary must be an object.")
    elif set(summary.keys()) != {"text", "evidence"}:
        issues.append(
            "Summary must contain exactly text and evidence."
        )
    else:
        validate_text(summary["text"], "Summary text")
        validate_evidence(summary["evidence"], "Summary evidence")

    # Validate observations.
    observations = payload["observations"]

    if not isinstance(observations, list):
        issues.append("Observations must be a list.")
    elif len(observations) > 4:
        issues.append("The response contains more than 4 observations.")
    else:
        for index, observation in enumerate(observations):
            name = f"Observation {index + 1}"

            if not isinstance(observation, dict):
                issues.append(f"{name} must be an object.")
                continue

            if set(observation.keys()) != {
                "title", "explanation", "evidence"
            }:
                issues.append(
                    f"{name} must contain title, explanation, "
                    "and evidence."
                )
                continue

            validate_text(observation["title"], f"{name} title")
            validate_text(
                observation["explanation"],
                f"{name} explanation"
            )
            validate_evidence(
                observation["evidence"],
                f"{name} evidence"
            )

    # Validate recommendations.
    recommendations = payload["recommendations"]

    if not isinstance(recommendations, list):
        issues.append("Recommendations must be a list.")
    elif len(recommendations) > 3:
        issues.append(
            "The response contains more than 3 recommendations."
        )
    else:
        for index, recommendation in enumerate(recommendations):
            name = f"Recommendation {index + 1}"

            if not isinstance(recommendation, dict):
                issues.append(f"{name} must be an object.")
                continue

            if set(recommendation.keys()) != {
                "action", "rationale", "evidence", "caveat"
            }:
                issues.append(
                    f"{name} must contain action, rationale, "
                    "evidence, and caveat."
                )
                continue

            validate_text(
                recommendation["action"],
                f"{name} action"
            )
            validate_text(
                recommendation["rationale"],
                f"{name} rationale"
            )
            validate_text(
                recommendation["caveat"],
                f"{name} caveat"
            )
            validate_evidence(
                recommendation["evidence"],
                f"{name} evidence"
            )

# Validate data quality interpretation.
    data_quality_interpretation = payload.get("data_quality_interpretation")

    if data_quality_interpretation is not None:
        if not isinstance(data_quality_interpretation, list):
            issues.append(
                "Data quality interpretation must be a list or null."
            )
        elif len(data_quality_interpretation) > 2:
            issues.append(
                "The response contains more than 2 data quality interpretation items."
            )
        else:
            for index, dqi in enumerate(data_quality_interpretation):
                name = f"Data quality interpretation {index + 1}"

                if not isinstance(dqi, dict):
                    issues.append(f"{name} must be an object.")
                    continue

                if set(dqi.keys()) != {"title", "explanation", "evidence"}:
                    issues.append(
                        f"{name} must contain title, explanation, "
                        "and evidence."
                    )
                    continue

                validate_text(dqi["title"], f"{name} title")
                validate_text(
                    dqi["explanation"],
                    f"{name} explanation"
                )
                validate_evidence(
                    dqi["evidence"],
                    f"{name} evidence"
                )
    else:
        data_quality_interpretation = None

    return issues