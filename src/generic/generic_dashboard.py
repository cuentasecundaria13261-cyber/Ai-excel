"""Streamlit page: upload, clean, explore and get AI insights for ANY dataset."""

import pandas as pd
import streamlit as st

from src.ai.ai_notice import ai_gate, render_ai_unavailable
from src.ai.ai_service import ai_status
from src.ai.prompt_builder import convert_to_json_safe
from src.business.sample_data import sample_upload
from src.security import upload_guard as ug
from src.security.privacy_ui import apply_personal_data_choice, render_privacy_note
from src.generic.generic_analysis import (
    MAX_DIMENSIONS,
    ROLES,
    aggregate_by_group,
    aggregate_by_period,
    build_generic_analytics,
    infer_column_roles,
    list_sheets,
    suggest_main_date,
    suggest_main_measure,
)
from src.generic.cached_io import clean_cached, read_cached
from src.generic.generic_insights import generate_generic_insights


def _md(text):
    """Escape '$' so Streamlit does not render money amounts as math."""
    return str(text).replace("$", "\\$")


def _evidence_line(evidence, facts):
    parts = []
    for fact_id in evidence or []:
        fact = facts.get(fact_id)
        if fact:
            path = str(fact["path"]).replace("analytics.", "", 1)
            parts.append(f"{fact_id}: {path} = {fact['value']}")
        else:
            parts.append(str(fact_id))
    return "; ".join(parts)


def _show_evidence(evidence, facts):
    line = _evidence_line(evidence, facts)
    if line:
        st.caption(_md(f"Evidence: {line}"))


def render_insights(result):
    """Display the AI report, with each claim linked to the facts behind it."""
    insights = result["insights"]
    facts = {fact["id"]: fact for fact in result["fact_catalog"]}

    if not result["structure_valid"]:
        st.warning("The AI response had some issues, but it is shown below.")
        with st.expander("Validation issues"):
            for issue in result["validation_issues"]:
                st.write(f"- {issue}")

    if not isinstance(insights, dict):
        st.error("The AI did not return a usable report. Please try again.")
        return

    st.subheader("Executive summary")
    summary = insights.get("executive_summary")
    if isinstance(summary, dict):
        st.write(_md(summary.get("text", "")))
        _show_evidence(summary.get("evidence"), facts)
    else:
        st.write("No summary generated.")

    st.subheader("Key observations")
    observations = insights.get("key_performance_observations", [])
    if observations:
        for obs in observations:
            st.markdown(_md(f"- **{obs.get('category', '')}**: {obs.get('analysis', '')}"))
            _show_evidence(obs.get("evidence"), facts)
    else:
        st.write("No significant observations identified.")

    st.subheader("Recommendations")
    recommendations = insights.get("business_recommendations", [])
    if recommendations:
        for rec in recommendations:
            st.markdown(_md(f"- **Action**: {rec.get('action', '')}"))
            st.caption(_md(f"Reason: {rec.get('reason', '')}"))
            st.caption(_md(f"Caveat: {rec.get('caveat', '')}"))
            _show_evidence(rec.get("evidence"), facts)
    else:
        st.write("No recommendations at this time.")

    st.subheader("Data quality")
    quality_items = insights.get("data_quality_interpretation", [])
    if quality_items:
        for item in quality_items:
            st.markdown(_md(f"- **{item.get('title', '')}**: {item.get('explanation', '')}"))
            _show_evidence(item.get("evidence"), facts)
    else:
        st.write("No data quality issues identified.")

    st.subheader("Further analysis opportunities")
    further = insights.get("further_analysis_opportunities", [])
    if further:
        for item in further:
            st.markdown(
                _md(
                    f"- **{item.get('question', '')}** "
                    f"(needs: {item.get('additional_data_required', '')})"
                )
            )
    else:
        st.write("No further analysis suggestions.")

    limitations = insights.get("analysis_limitations", [])
    if limitations:
        st.subheader("Analysis limitations")
        for limitation in limitations:
            st.markdown(_md(f"- {limitation}"))

    st.caption(
        "AI-generated from the calculated facts. Check important numbers "
        "against the tables and charts above."
    )


def render_generic_dashboard():
    st.title("Generic Dashboard")
    st.write(
        "Upload any Excel or CSV file. The app detects what each column is, "
        "cleans the data and explains it with AI, whatever the columns are."
    )

    uploaded = st.file_uploader(
        "Choose an Excel or CSV file",
        type=["csv", "xlsx", "xlsm"],
        key="generic_dataset_uploader",
    )
    render_privacy_note()

    if uploaded is not None:
        st.session_state["generic_use_sample"] = False
    else:
        use_sample = st.session_state.get("generic_use_sample", False)
        if not use_sample:
            st.info("Upload a file to get started.")
            if st.button("Try it with sample data", key="generic_sample_btn"):
                st.session_state["generic_use_sample"] = True
                use_sample = True
        if not use_sample:
            return
        uploaded = sample_upload()
        st.caption("You are looking at made-up sample data. Upload your own file above to analyze it.")

    file_bytes = uploaded.getvalue()
    file_id = f"{uploaded.name}:{len(file_bytes)}"

    # ---- 1. Read
    sheet_name = None
    if uploaded.name.lower().endswith((".xlsx", ".xlsm")):
        try:
            sheets = list_sheets(file_bytes)
        except Exception as error:
            st.error(f"Could not open the Excel file: {error}")
            return
        if len(sheets) > 1:
            sheet_name = st.selectbox("Sheet to analyze", sheets, key=f"generic_sheet_{file_id}")
        else:
            sheet_name = sheets[0]

    with st.expander("Reading options"):
        header_row = int(
            st.number_input(
                "Header row (1 = first row of the sheet)",
                min_value=1,
                max_value=50,
                value=1,
                step=1,
                key=f"generic_header_{file_id}",
            )
        ) - 1

    try:
        raw_df = read_cached(file_bytes, uploaded.name, sheet_name, header_row)
    except Exception as error:
        st.error(f"Could not read the file: {error}")
        return

    if raw_df.empty:
        st.warning("The file was read, but it has no data rows.")
        return

    st.success("File uploaded and read successfully!")
    large_note = ug.large_file_note(len(raw_df))
    if large_note:
        st.info(large_note)
    st.dataframe(raw_df.head(100))

    # ---- 2. Clean
    st.subheader("Data cleaning")
    left, right = st.columns(2)
    with left:
        remove_duplicates = st.checkbox(
            "Remove duplicate rows", value=True, key=f"generic_dups_{file_id}"
        )
        convert_numbers = st.checkbox(
            "Convert numbers stored as text (for example $1,200)",
            value=True,
            key=f"generic_nums_{file_id}",
        )
        parse_dates = st.checkbox(
            "Detect and convert date columns", value=True, key=f"generic_dates_{file_id}"
        )
    with right:
        missing_strategy = st.selectbox(
            "How should missing values be handled?",
            options=["keep", "drop", "fill"],
            format_func=lambda x: {
                "keep": "Keep missing values",
                "drop": "Drop rows with missing values",
                "fill": "Fill (median for numbers, 'Unknown' for text)",
            }[x],
            key=f"generic_missing_{file_id}",
        )
        date_order = st.selectbox(
            "Order of day and month in text dates",
            options=["auto", "day_first", "month_first"],
            format_func=lambda x: {
                "auto": "Detect automatically",
                "day_first": "Day first (31/12/2024)",
                "month_first": "Month first (12/31/2024)",
            }[x],
            key=f"generic_dateorder_{file_id}",
        )

    cleaned_df, report = clean_cached(
        raw_df,
        remove_duplicates=remove_duplicates,
        convert_numbers=convert_numbers,
        parse_dates=parse_dates,
        missing_strategy=missing_strategy,
        date_order=date_order,
    )

    if cleaned_df.empty:
        st.error("No rows are left after cleaning. Try keeping the missing values.")
        return

    cleaned_df, removed_personal = apply_personal_data_choice(cleaned_df, f"generic_pii_{file_id}")
    if cleaned_df.shape[1] == 0:
        st.error("No columns are left after removing personal data. Untick the box to keep them, or upload a different file.")
        return
    if removed_personal:
        report = [*report, f"Removed columns that look like personal data: {', '.join(str(c) for c in removed_personal)}."]

    with st.expander("What the cleaning did", expanded=True):
        for action in report:
            st.write(f"- {action}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Original rows", len(raw_df))
    col2.metric("Cleaned rows", len(cleaned_df))
    col3.metric("Columns", len(cleaned_df.columns))

    with st.expander("Cleaned dataset preview"):
        st.dataframe(cleaned_df.head(100))

    st.download_button(
        label="Download Cleaned CSV",
        data=ug.to_safe_csv_bytes(cleaned_df),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        key=f"generic_download_{file_id}",
    )

    # ---- 3. Column roles
    st.subheader("Column roles")
    st.caption(
        "The app guessed what each column is. Change any that look wrong: "
        "measure = a number to analyze, dimension = a category to group by, "
        "date = a time column, id / text / ignore = not used for comparisons."
    )

    inferred = infer_column_roles(cleaned_df)
    signature = abs(hash((file_id, missing_strategy, tuple(inferred.items()))))

    roles_table = pd.DataFrame({"Column": list(inferred.keys()), "Role": list(inferred.values())})
    edited = st.data_editor(
        roles_table,
        column_config={
            "Role": st.column_config.SelectboxColumn("Role", options=ROLES, required=True),
        },
        disabled=["Column"],
        hide_index=True,
        key=f"generic_roles_{signature}",
    )
    roles = dict(zip(edited["Column"], edited["Role"]))

    # ---- 4. Analysis settings
    measures = [c for c, r in roles.items() if r == "measure"]
    dates = [c for c, r in roles.items() if r == "date"]
    dimensions = sorted(
        [c for c, r in roles.items() if r == "dimension"],
        key=lambda c: cleaned_df[c].nunique(),
    )

    role_signature = abs(hash((signature, tuple(sorted(roles.items())))))

    st.subheader("Analysis settings")
    left, middle, right = st.columns(3)

    with left:
        if measures:
            suggested = suggest_main_measure(cleaned_df, roles)
            main_measure = st.selectbox(
                "Main metric",
                measures,
                index=measures.index(suggested) if suggested in measures else 0,
                key=f"generic_measure_{role_signature}",
            )
        else:
            main_measure = None
            st.info("No numeric column found, so only record counts will be analyzed.")

    with middle:
        if dates:
            suggested_date = suggest_main_date(cleaned_df, roles)
            main_date = st.selectbox(
                "Date column",
                dates,
                index=dates.index(suggested_date) if suggested_date in dates else 0,
                key=f"generic_date_{role_signature}",
            )
        else:
            main_date = None
            st.info("No date column found, so time trends will be skipped.")

    with right:
        aggregation = st.selectbox(
            "How to combine values in a group",
            options=["sum", "mean"],
            format_func=lambda x: "Total (sum)" if x == "sum" else "Average (mean)",
            key=f"generic_agg_{role_signature}",
        )

    chosen_dimensions = st.multiselect(
        "Columns to compare (groups)",
        options=dimensions,
        default=dimensions[:MAX_DIMENSIONS],
        key=f"generic_dims_{role_signature}",
    )

    # ---- 5. Analytics and charts
    try:
        analytics = build_generic_analytics(
            cleaned_df,
            roles,
            main_measure=main_measure,
            main_date=main_date,
            dimensions=chosen_dimensions,
            aggregation=aggregation,
        )
    except Exception as error:
        st.error(f"Could not calculate the analytics: {error}")
        return

    st.subheader("Overview")
    metric_cols = st.columns(3)
    metric_cols[0].metric("Rows", analytics["overview"]["rows"])
    metric_cols[1].metric("Columns", analytics["overview"]["columns"])
    if main_measure and main_measure in analytics["measures"]:
        stats = analytics["measures"][main_measure]
        metric_cols[2].metric(f"Total {main_measure}", stats["total"])
        st.write(
            f"{main_measure}: average {stats['average']}, median {stats['median']}, "
            f"minimum {stats['minimum']}, maximum {stats['maximum']}."
        )

    for dimension in chosen_dimensions[:2]:
        st.markdown(_md(f"**{main_measure or 'Records'} by {dimension}**"))
        if main_measure:
            grouped = aggregate_by_group(cleaned_df, dimension, main_measure, aggregation)
        else:
            grouped = cleaned_df[dimension].value_counts()
        if not grouped.empty:
            st.bar_chart(grouped.head(10))

    if main_date:
        monthly = aggregate_by_period(cleaned_df, main_date, main_measure, aggregation, "M")
        if len(monthly) >= 2:
            st.markdown(_md(f"**{main_measure or 'Records'} by month**"))
            st.line_chart(monthly)

    with st.expander("Calculated facts (what the AI receives)"):
        st.json(convert_to_json_safe(analytics))

    # ---- 6. AI insights
    st.divider()
    st.header("AI Insights")

    status = ai_status()
    goal = ""
    description = ""
    if status["available"]:
        goal = st.text_input(
            "What do you want to learn? (optional)",
            key=f"generic_goal_{file_id}",
            placeholder="For example: which groups should we focus on?",
        )
        description = st.text_input(
            "Short description of this dataset (optional)",
            key=f"generic_description_{file_id}",
            placeholder="For example: monthly support tickets of a software company",
        )
    else:
        render_ai_unavailable(status)

    if status["available"] and ai_gate(status, "generic") and st.button("Generate AI Insights", key="generic_generate_ai_btn"):
        with st.spinner("Generating AI insights..."):
            try:
                result = generate_generic_insights(analytics, goal=goal, description=description)
                st.session_state["generic_ai_result"] = {"file_id": file_id, "result": result}
            except Exception as error:
                st.session_state.pop("generic_ai_result", None)
                st.error(f"Error generating AI insights: {error}")

    stored = st.session_state.get("generic_ai_result")
    if stored and stored["file_id"] == file_id:
        st.caption("Generated from the settings you had when you clicked the button.")
        render_insights(stored["result"])
