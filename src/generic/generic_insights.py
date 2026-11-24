"""AI insights for any dataset (the generic counterpart of insight_generator.py)."""

import json
import re

from src.ai.ai_service import generate_response
from src.ai.insight_validator import validate_insight_payload
from src.ai.prompt_builder import build_fact_catalog
from src.i18n import language_instruction
from src.security.upload_guard import sanitize_label


def build_generic_prompt(analytics, goal="", description=""):
    """Build a prompt that works for any dataset, using only Python-calculated facts."""

    facts = build_fact_catalog(analytics)
    facts_text = "\n".join(
        f"{fact['id']} | {fact['path']} = {fact['value']}"
        for fact in facts
    )

    # Text typed by the visitor goes into the prompt: keep it to short plain lines.
    goal = sanitize_label(goal, 700)
    description = sanitize_label(description, 300)

    context_lines = []
    if description.strip():
        context_lines.append(f"Dataset description from the user: {description.strip()}")
    if goal.strip():
        context_lines.append(f"What the user wants to learn: {goal.strip()}")
    context = "\n".join(context_lines) or "No extra context was provided."

    language_line = language_instruction()
    return f"""
You are a careful data analyst. The dataset can be about anything (sales, people,
operations, science, finance...). Write insights and recommendations based ONLY
on the facts below. Each line is: ID | path = value.

CONTEXT:
{context}

FACTS (calculated by Python, the only source of truth):
{facts_text}

HOW TO READ THE FACTS:
- analytics.overview.settings.main_metric is the column being analysed, and
  aggregation_used says whether group values are totals (sum) or averages (mean).
- analytics.by_group.<column>.top_groups.<name> = value means that group <name>
  of <column> has that value of the main metric. The last part of a path is the name.
- analytics.time.by_month keys look like 2024-03 (year-month). The most recent
  period may be incomplete.
- Do not assume a currency or a unit that the column names do not state.

RULES FOR NUMBERS AND NAMES:
1. Include specific numbers in your text, but ONLY numbers that appear in the facts.
   Copy them exactly (you may add thousands separators).
2. Do NOT calculate new numbers. No new percentages, totals, averages or differences
   unless a fact already gives that value.
3. Always name the specific columns and groups you refer to, exactly as they
   appear in the facts.
4. If something has no data, say it is not available. Never invent facts, trends
   or causes. Correlation is not causation.
5. Keep every text field short: one or two sentences.
6. If the user gave a goal, focus the observations and recommendations on it.

WRITE FOR A PERSON WHO IS NOT TECHNICAL:
- Imagine the reader is a shop owner or a student who has never used data tools.
  Use short, everyday words and explain what the numbers MEAN for them.
- Do NOT mention technical details: no number of rows or columns, no file or table
  structure, no column type names, no fact IDs, no variable or path names such as
  "overview.rows" or "by_group", no words like "dataset", "field", "variable",
  "schema", "null", "outlier", "correlation coefficient" or "aggregation".
  Say "your sales", "your products", "your customers" or "your data" instead.
- Do not describe how big the file is. Start with what happened and what to do.
- Use column and group names only when they help the reader (for example a product
  or a region), written the way the reader knows them.
- Explain any unavoidable technical idea in one simple sentence.

EVIDENCE:
- Every evidence list must contain real fact IDs from the list above.
  Never invent IDs.

OUTPUT:
Return ONLY valid JSON. No Markdown fences, no extra text.
Use exactly this structure:

{{
  "executive_summary": {{
    "text": "Two short, plain sentences on what the numbers mean for the reader, quoting key numbers from the facts. No row or column counts.",
    "evidence": ["<fact id>"]
  }},
  "key_performance_observations": [
    {{
      "category": "Big picture",
      "analysis": "The main number and how it looks overall, in plain words (no file size, no row or column counts).",
      "evidence": ["<fact id>"]
    }},
    {{
      "category": "Top and bottom groups",
      "analysis": "Which groups lead or lag on the main metric, by name, with values.",
      "evidence": ["<fact id>", "<fact id>"]
    }},
    {{
      "category": "Time trend",
      "analysis": "Strongest and weakest periods, if date facts exist.",
      "evidence": ["<fact id>"]
    }},
    {{
      "category": "Relationships",
      "analysis": "Notable relationships between numeric columns, if facts exist.",
      "evidence": ["<fact id>"]
    }}
  ],
  "business_recommendations": [
    {{
      "action": "A practical, specific action.",
      "reason": "The observation and numbers that support it.",
      "evidence": ["<fact id>"],
      "caveat": "What the available data cannot establish."
    }}
  ],
  "data_quality_interpretation": [
    {{
      "title": "Short issue title",
      "explanation": "Why this limits what we can say, in plain words.",
      "evidence": ["<fact id>"]
    }}
  ],
  "further_analysis_opportunities": [
    {{
      "question": "A question this dataset cannot answer.",
      "additional_data_required": "The data needed to answer it."
    }}
  ],
  "analysis_limitations": [
    "What the dataset cannot establish, including unsupported causal conclusions."
  ]
}}

LIMITS:
- At most 5 key_performance_observations, 3 business_recommendations,
  2 data_quality_interpretation items and 3 further_analysis_opportunities.
- Use an empty list when nothing useful can be supported.
- Do not add extra JSON keys.
{language_line}
"""


def parse_json_response(text):
    """Parse the model output, tolerating <think> blocks and Markdown fences."""

    if not isinstance(text, str):
        raise ValueError("The AI response was not text.")

    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in the AI response.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as error:
            raise ValueError(f"The AI response was not valid JSON: {error}") from error


def generate_generic_insights(
    analytics,
    goal="",
    description="",
    strict_mode=False,
    max_attempts=2,
):
    """Generate and validate AI insights for any dataset's analytics."""

    prompt = build_generic_prompt(analytics, goal, description)

    payload = None
    last_error = None
    for _ in range(max_attempts):
        response = generate_response(prompt)
        try:
            payload = parse_json_response(response)
            break
        except ValueError as error:
            last_error = error

    if payload is None:
        raise RuntimeError(
            f"The AI did not return valid JSON after {max_attempts} attempts "
            f"({last_error}). Try again, or try a larger model."
        )

    fact_catalog = build_fact_catalog(analytics)
    known_fact_ids = {fact["id"] for fact in fact_catalog}

    issues = validate_insight_payload(payload, known_fact_ids, strict_mode=strict_mode)

    return {
        "insights": payload,
        "fact_catalog": fact_catalog,
        "validation_issues": issues,
        "structure_valid": len(issues) == 0,
    }
