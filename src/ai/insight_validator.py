def validate_insight_payload(payload, known_fact_ids, strict_mode=True):
    """Validate the structure and evidence references in an AI response.

    strict_mode is kept for compatibility; numbers in text are now allowed.
    """

    issues = []

    if not isinstance(payload, dict):
        return ["The AI response must be a JSON object."]

    # Validate executive_summary
    if "executive_summary" not in payload:
        issues.append("Missing required section: executive_summary")
    else:
        es = payload["executive_summary"]
        if not isinstance(es, dict):
            issues.append("executive_summary must be an object.")
        elif set(es.keys()) != {"text", "evidence"}:
            issues.append("executive_summary must contain text and evidence.")
        else:
            if not isinstance(es["text"], str) or not es["text"].strip():
                issues.append("executive_summary.text must be a non-empty string.")
            if isinstance(es["text"], str) and len(es["text"]) > 700:
                issues.append("executive_summary.text is too long.")
            if not isinstance(es["evidence"], list) or not es["evidence"]:
                issues.append("executive_summary.evidence must contain at least one fact ID.")
            else:
                for fid in es["evidence"]:
                    if not isinstance(fid, str) or fid not in known_fact_ids:
                        issues.append(f"executive_summary.evidence references unknown fact ID: {fid}.")

    # Validate key_performance_observations
    observations = payload.get("key_performance_observations", [])
    if not isinstance(observations, list):
        issues.append("key_performance_observations must be a list.")
    elif len(observations) > 5:
        issues.append("key_performance_observations must not exceed 5 items.")
    else:
        for i, obs in enumerate(observations):
            if not isinstance(obs, dict):
                issues.append(f"key_performance_observations[{i}] must be an object.")
                continue
            if set(obs.keys()) != {"category", "analysis", "evidence"}:
                issues.append(f"key_performance_observations[{i}] must contain category, analysis, and evidence.")
                continue
            if not isinstance(obs.get("category"), str) or not obs["category"].strip():
                issues.append(f"key_performance_observations[{i}].category must be a non-empty string.")
            if not isinstance(obs.get("analysis"), str) or not obs["analysis"].strip():
                issues.append(f"key_performance_observations[{i}].analysis must be a non-empty string.")
            if not isinstance(obs.get("evidence"), list) or not obs["evidence"]:
                issues.append(f"key_performance_observations[{i}].evidence must contain at least one fact ID.")
            else:
                for fid in obs["evidence"]:
                    if not isinstance(fid, str) or fid not in known_fact_ids:
                        issues.append(f"key_performance_observations[{i}].evidence references unknown fact ID: {fid}.")

    # Validate business_recommendations
    recommendations = payload.get("business_recommendations", [])
    if not isinstance(recommendations, list):
        issues.append("business_recommendations must be a list.")
    elif len(recommendations) > 3:
        issues.append("business_recommendations must not exceed 3 items.")
    else:
        for i, rec in enumerate(recommendations):
            if not isinstance(rec, dict):
                issues.append(f"business_recommendations[{i}] must be an object.")
                continue
            if set(rec.keys()) != {"action", "reason", "evidence", "caveat"}:
                issues.append(f"business_recommendations[{i}] must contain action, reason, evidence, and caveat.")
                continue
            for field in ["action", "reason", "caveat"]:
                if not isinstance(rec.get(field), str) or not rec[field].strip():
                    issues.append(f"business_recommendations[{i}].{field} must be a non-empty string.")
            if not isinstance(rec.get("evidence"), list) or not rec["evidence"]:
                issues.append(f"business_recommendations[{i}].evidence must contain at least one fact ID.")
            else:
                for fid in rec["evidence"]:
                    if not isinstance(fid, str) or fid not in known_fact_ids:
                        issues.append(f"business_recommendations[{i}].evidence references unknown fact ID: {fid}.")

    # Validate data_quality_interpretation
    dqi = payload.get("data_quality_interpretation", [])
    if not isinstance(dqi, list):
        issues.append("data_quality_interpretation must be a list or not present.")
    elif len(dqi) > 2:
        issues.append("data_quality_interpretation must not exceed 2 items.")
    else:
        for i, item in enumerate(dqi):
            if not isinstance(item, dict):
                issues.append(f"data_quality_interpretation[{i}] must be an object.")
                continue
            if set(item.keys()) != {"title", "explanation", "evidence"}:
                issues.append(f"data_quality_interpretation[{i}] must contain title, explanation, and evidence.")
                continue
            if not isinstance(item.get("title"), str) or not item["title"].strip():
                issues.append(f"data_quality_interpretation[{i}].title must be a non-empty string.")
            if not isinstance(item.get("explanation"), str) or not item["explanation"].strip():
                issues.append(f"data_quality_interpretation[{i}].explanation must be a non-empty string.")
            if not isinstance(item.get("evidence"), list) or not item["evidence"]:
                issues.append(f"data_quality_interpretation[{i}].evidence must contain at least one fact ID.")
            else:
                for fid in item["evidence"]:
                    if not isinstance(fid, str) or fid not in known_fact_ids:
                        issues.append(f"data_quality_interpretation[{i}].evidence references unknown fact ID: {fid}.")

    # Validate further_analysis_opportunities
    fao = payload.get("further_analysis_opportunities", [])
    if not isinstance(fao, list):
        issues.append("further_analysis_opportunities must be a list or not present.")
    elif len(fao) > 3:
        issues.append("further_analysis_opportunities must not exceed 3 items.")
    else:
        for i, item in enumerate(fao):
            if not isinstance(item, dict):
                issues.append(f"further_analysis_opportunities[{i}] must be an object.")
                continue
            if set(item.keys()) != {"question", "additional_data_required"}:
                issues.append(f"further_analysis_opportunities[{i}] must contain question and additional_data_required.")
                continue
            if not isinstance(item.get("question"), str) or not item["question"].strip():
                issues.append(f"further_analysis_opportunities[{i}].question must be a non-empty string.")
            if not isinstance(item.get("additional_data_required"), str) or not item["additional_data_required"].strip():
                issues.append(f"further_analysis_opportunities[{i}].additional_data_required must be a non-empty string.")

    return issues