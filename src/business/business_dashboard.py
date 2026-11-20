"""Business Dashboard page: for people who never open Excel.

Upload a file -> it is tidied automatically -> the columns are matched -> you get
a plain-language summary, alerts, key numbers with comparisons, charts, an
optional AI explanation and a report you can download.
"""

import pandas as pd
import streamlit as st

from src.ai.ai_notice import ai_gate, render_ai_unavailable
from src.ai.ai_service import ai_status
from src.business import business_engine as be
from src.business import business_report as br
from src.business.sample_data import sample_upload
from src.generic import generic_analysis as ga
from src.generic.cached_io import clean_cached, read_cached
from src.generic.generic_dashboard import render_insights
from src.generic.generic_insights import generate_generic_insights
from src.i18n import get_language, t
from src.security import upload_guard as ug
from src.security.privacy_ui import apply_personal_data_choice, render_privacy_note

NONE_OPTION = "(none)"

AI_BASE_GOAL = (
    "Write for a busy business owner with no data background: short sentences, "
    "plain words, and say what to do next. Use analytics.comparison (the latest "
    "period against the one before) and analytics.alerts when they exist."
)


def _md(text):
    """Escape '$' so Streamlit does not turn money amounts into math."""
    return str(text).replace("$", "\\$")


def _read_uploads(uploads):
    """Read one or more uploaded files into one DataFrame. Returns (df, notes, file_id)."""
    notes = []
    frames = []
    file_parts = []

    single_excel = len(uploads) == 1 and uploads[0].name.lower().endswith((".xlsx", ".xlsm"))

    for upload in uploads:
        data = upload.getvalue()
        file_parts.append(f"{upload.name}:{len(data)}")
        sheet = None

        if upload.name.lower().endswith((".xlsx", ".xlsm")):
            sheets = ga.list_sheets(data)
            if single_excel and len(sheets) > 1:
                sheet = st.selectbox(
                    t("Which sheet has your sales?"),
                    sheets,
                    key=f"biz_sheet_{upload.name}_{len(data)}",
                )
            else:
                sheet = sheets[0]
                if len(sheets) > 1:
                    notes.append(t("{name}: used the first sheet ('{sheet}').", name=upload.name, sheet=sheet))

        frames.append(read_cached(data, upload.name, sheet))

    if len(frames) == 1:
        return frames[0], notes, "|".join(file_parts)

    first_columns = list(frames[0].columns)
    if any(list(frame.columns) != first_columns for frame in frames[1:]):
        notes.append(t("The files do not have exactly the same columns. Columns that are missing in a file are left empty."))
    combined = pd.concat(frames, ignore_index=True, sort=False)
    ug.check_frame(combined)   # several files together must still fit the free demo
    notes.append(t("Combined {files} files into one table of {rows} rows.", files=len(frames), rows=len(combined)))
    return combined, notes, "|".join(file_parts)


def _bar(series, title):
    st.markdown(f"**{_md(title)}**")
    chart = series.astype(float).copy()
    chart.index = [str(name) for name in chart.index]
    st.bar_chart(chart)


def _show_alert(alert):
    text = f"**{_md(alert['title'])}**  \n{_md(alert['detail'])}"
    if alert["severity"] == "high":
        st.error(text)
    elif alert["severity"] == "medium":
        st.warning(text)
    else:
        st.info(text)


def render_business_dashboard():
    st.title(t("Business Dashboard"))
    st.write(
        t("Upload your sales file. We tidy it, draw the charts and tell you what needs "
          "your attention - no Excel skills needed.")
    )

    uploads = st.file_uploader(
        t("Choose one or more Excel or CSV files"),
        type=["csv", "xlsx", "xlsm"],
        accept_multiple_files=True,
        key="business_uploader",
    )
    render_privacy_note()
    if uploads:
        st.session_state["biz_use_sample"] = False
    else:
        use_sample = st.session_state.get("biz_use_sample", False)
        if not use_sample:
            st.info(t("Upload a file to get started. Any column names work - we match them for you."))
            if st.button(t("Try it with sample data"), key="biz_sample_btn"):
                st.session_state["biz_use_sample"] = True
                use_sample = True
        if not use_sample:
            return
        uploads = [sample_upload()]
        st.caption(t("You are looking at made-up sample data. Upload your own file above to analyze it."))

    # ---- 1. Read and tidy automatically
    try:
        raw_df, read_notes, file_id = _read_uploads(uploads)
    except ug.UploadRejected as error:
        st.error(str(error))
        return
    except Exception as error:
        st.error(t("Could not read the file: {error}", error=error))
        return

    if raw_df.empty:
        st.warning(t("The file was read, but it has no data rows."))
        return

    large_note = ug.large_file_note(len(raw_df))
    if large_note:
        st.info(large_note)

    cleaned, clean_report = clean_cached(
        raw_df,
        language=get_language(),
        remove_duplicates=False,   # duplicates are handled once the order number is known
        convert_numbers=True,
        parse_dates=True,
        missing_strategy="keep",
    )
    if cleaned.empty:
        st.error(t("No data is left after tidying the file."))
        return

    cleaned, removed_personal = apply_personal_data_choice(cleaned, f"biz_pii_{file_id}")
    if cleaned.shape[1] == 0:
        st.error(t("No columns are left after removing personal data. Untick the box to keep them, or upload a different file."))
        return
    privacy_notes = (
        [t("Removed columns that look like personal data: {columns}.", columns=", ".join(str(c) for c in removed_personal))]
        if removed_personal else []
    )

    # ---- 2. Match the columns
    roles = ga.infer_column_roles(cleaned)
    guess = be.guess_mapping(cleaned, roles)
    columns = list(cleaned.columns)
    file_sig = abs(hash((file_id, tuple(columns))))

    needs_attention = guess["revenue"] is None and not (guess["quantity"] and guess["unit_price"])

    with st.expander(t("We matched your columns - check them"), expanded=needs_attention):
        st.caption(t("Change a choice if we guessed wrong. Only the money column is really needed."))
        options = [NONE_OPTION] + columns
        mapping = {}
        pickers = st.columns(2)
        for i, field in enumerate(be.FIELDS):
            default = guess[field] if guess[field] in columns else NONE_OPTION
            choice = pickers[i % 2].selectbox(
                t(be.FIELD_LABELS[field]),
                options,
                index=options.index(default),
                key=f"biz_map_{field}_{file_sig}",
                format_func=lambda value: t("(none)") if value == NONE_OPTION else value,
            )
            mapping[field] = None if choice == NONE_OPTION else choice

        chosen = [c for c in mapping.values() if c]
        if len(chosen) != len(set(chosen)):
            st.warning(t("The same column is used for two different things. Check your choices."))

    work_all, prep_notes, metric_label = be.prepare_frame(cleaned, mapping)
    if work_all.empty:
        st.error(t("There is no data to analyze after matching the columns."))
        return

    with st.expander(t("What we tidied in your file")):
        for line in [*read_notes, *clean_report, *privacy_notes, *prep_notes]:
            st.write(f"- {_md(line)}")
        st.write("- " + t("{read} rows read, {used} rows used.", read=len(raw_df), used=len(work_all)))

    # ---- 3. Filters
    filter_parts = []
    date_range = None
    regions = categories = products = None

    with st.expander(t("Filter your data (optional)")):
        if "date" in work_all and work_all["date"].notna().any():
            low, high = work_all["date"].min().date(), work_all["date"].max().date()
            picked = st.date_input(
                t("Dates"),
                value=(low, high),
                min_value=low,
                max_value=high,
                key=f"biz_dates_{file_sig}",
            )
            if isinstance(picked, (tuple, list)) and len(picked) == 2 and tuple(picked) != (low, high):
                date_range = (picked[0], picked[1])
                filter_parts.append(t("Dates: {start} to {end}", start=picked[0], end=picked[1]))

        for field, label in (("region", t("Region")), ("category", t("Category")), ("product", t("Product"))):
            if field in work_all:
                values = sorted(work_all[field].dropna().astype(str).unique().tolist())
                if 1 < len(values) <= 500:
                    selected = st.multiselect(label, values, key=f"biz_{field}_{file_sig}")
                    if selected:
                        filter_parts.append(f"{label}: {', '.join(selected)}")
                        if field == "region":
                            regions = selected
                        elif field == "category":
                            categories = selected
                        else:
                            products = selected

    work = be.apply_filters(work_all, date_range, regions, categories, products)
    filters_text = "; ".join(filter_parts)
    if work.empty:
        st.warning(t("No rows match these filters. Clear a filter above."))
        return

    # ---- 4. Calculate everything
    kpis = be.compute_kpis(work)
    periods = be.split_periods(work)
    comparison = be.compare_periods(periods) if periods else None
    alerts = be.build_alerts(work, periods, comparison, metric_label)
    summary_lines = be.build_summary(work, kpis, periods, comparison, alerts, metric_label)

    # ---- 5. What happened
    st.header(t("What happened"))
    if filters_text:
        st.caption(_md(t("Filtered: {filters}", filters=filters_text)))
    for line in summary_lines:
        st.markdown(_md(f"- {line}"))

    # ---- 6. Alerts
    st.subheader(t("Things to look at"))
    if alerts:
        for alert in alerts:
            _show_alert(alert)
    else:
        st.success(t("Nothing unusual was detected."))

    # ---- 7. Key numbers
    st.subheader(t("Key numbers"))
    changes = comparison["change_pct"] if comparison else {}

    def delta(key):
        value = changes.get(key)
        return None if value is None else f"{be.fmt_pct(value)} " + t("vs previous period")

    items = [
        (t("Total {label}", label=t(metric_label).lower()), be.fmt_number(kpis["revenue"]), delta("revenue")),
        (t("Orders") if "order_id" in work else t("Records"), be.fmt_number(kpis["orders"]), delta("orders")),
        (t("Average per order"), be.fmt_number(kpis["average_order_value"]), delta("average_order_value")),
    ]
    if "units_sold" in kpis:
        items.append((t("Units sold"), be.fmt_number(kpis["units_sold"]), delta("units_sold")))

    cards = st.columns(len(items))
    for column, (label, value, change) in zip(cards, items):
        column.metric(label, value, delta=change)

    if periods:
        st.caption(
            t("Changes compare the last {days} days ({current}) with the {days} days before ({previous}).",
              days=periods["length_days"], current=periods["current_label"], previous=periods["previous_label"])
        )
    else:
        st.caption(t("There is not enough dated data to compare periods."))

    # ---- 8. Charts
    st.subheader(t("Charts"))
    label = t(metric_label).lower()

    time_series, time_unit = be.chart_over_time(work)
    products_series = be.top_n(work, "product")
    regions_series = be.top_n(work, "region")
    categories_series = be.top_n(work, "category")
    weekday_series = be.chart_by_weekday(work)

    tabs_spec = []
    if time_series is not None and len(time_series) >= 2:
        tabs_spec.append((t("Over time"), "time"))
    if products_series is not None:
        tabs_spec.append((t("Products"), "product"))
    if regions_series is not None:
        tabs_spec.append((t("Regions"), "region"))
    if categories_series is not None:
        tabs_spec.append((t("Categories"), "category"))
    if weekday_series is not None and weekday_series.sum() != 0:
        tabs_spec.append((t("Days of the week"), "weekday"))

    if tabs_spec:
        for tab, (_, kind) in zip(st.tabs([name for name, _ in tabs_spec]), tabs_spec):
            with tab:
                if kind == "time":
                    st.markdown("**" + t("How much {label} you made, by {unit}", label=label, unit=t(time_unit)) + "**")
                    st.line_chart(time_series.astype(float))
                elif kind == "product":
                    _bar(products_series, t("Which products bring in the most {label}", label=label))
                elif kind == "region":
                    _bar(regions_series, t("Which regions bring in the most {label}", label=label))
                elif kind == "category":
                    _bar(categories_series, t("Which categories bring in the most {label}", label=label))
                else:
                    _bar(weekday_series, t("Which days of the week sell the most ({label})", label=label))
    else:
        st.info(t("Match a date, product or region column above to see charts."))

    # ---- 9. AI explanation
    st.divider()
    st.header(t("Explain it to me (AI)"))
    st.caption(
        t("The AI reads the numbers above and explains them in plain words. "
          "It can make mistakes, so check anything important against the numbers.")
    )
    status = ai_status()
    goal = ""
    if status["available"]:
        goal = st.text_input(
            t("Is there something you want to know? (optional)"),
            key=f"biz_goal_{file_sig}",
            placeholder=t("For example: why are sales going down?"),
        )
    else:
        render_ai_unavailable(status)

    settings_key = str((file_sig, sorted((k, str(v)) for k, v in mapping.items()), filters_text))

    if status["available"] and ai_gate(status, "business") and st.button(t("Explain with AI"), key="business_ai_btn"):
        with st.spinner(t("The AI is reading your numbers...")):
            try:
                analytics = be.build_ai_analytics(work, periods, comparison, alerts, metric_label)
                full_goal = AI_BASE_GOAL + (f" The owner asks: {goal.strip()}" if goal.strip() else "")
                result = generate_generic_insights(
                    analytics,
                    goal=full_goal,
                    description="Sales data of a business.",
                )
                st.session_state["business_ai_result"] = {"settings": settings_key, "result": result}
            except Exception as error:
                st.session_state.pop("business_ai_result", None)
                st.error(t("Error generating AI insights: {error}", error=error))

    stored = st.session_state.get("business_ai_result")
    ai_for_report = None
    if stored:
        if stored["settings"] == settings_key:
            ai_for_report = stored["result"]
        else:
            st.caption(t("This explanation was made for a different file, columns or filters than the ones selected now."))
        render_insights(stored["result"])

    # ---- 10. Download the report
    st.divider()
    st.subheader(t("Take it with you"))

    charts_for_report = {
        t("Best products"): products_series,
        t("Regions"): regions_series,
        t("Categories"): categories_series,
        t("Days of the week"): weekday_series,
    }
    charts_for_report = {
        name: series for name, series in charts_for_report.items() if series is not None and len(series)
    }

    report_args = dict(
        title=t("Business report"),
        summary_lines=summary_lines,
        kpis=kpis,
        comparison=comparison,
        periods=periods,
        alerts=alerts,
        metric_label=metric_label,
        charts=charts_for_report,
        ai_result=ai_for_report,
        filters_text=filters_text,
    )

    left, right = st.columns(2)
    html_report = br.build_report_html(time_series=time_series, time_unit=time_unit, **report_args)
    left.download_button(
        t("Download report (web page)"),
        data=html_report.encode("utf-8"),
        file_name="business_report.html",
        mime="text/html",
        key=f"biz_dl_html_{file_sig}",
    )

    pdf_bytes = None
    try:
        pdf_bytes = br.build_report_pdf(**report_args)
    except Exception as error:
        right.caption(t("The PDF could not be created: {error}", error=error))

    if pdf_bytes:
        right.download_button(
            t("Download report (PDF)"),
            data=pdf_bytes,
            file_name="business_report.pdf",
            mime="application/pdf",
            key=f"biz_dl_pdf_{file_sig}",
        )
    elif not br.pdf_available():
        right.caption(
            t("For a PDF file: open the web page report and choose Print, then Save as PDF. "
              "Or install the optional package with: pip install reportlab")
        )

    st.download_button(
        t("Download the tidied data (CSV)"),
        data=ug.to_safe_csv_bytes(cleaned),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        key=f"biz_dl_csv_{file_sig}",
    )
