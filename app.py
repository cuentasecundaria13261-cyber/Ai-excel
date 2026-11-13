
import streamlit as st
 
from src.data.data_reader import read_file
from src.data.data_validator import validate_dataset
from src.data.data_cleaner import clean_dataset
from src.ai.insight_generator import generate_business_insights
 
# Page configuration
st.set_page_config(
    page_title="AI Excel Dashboard",
    page_icon="📊",
    layout="wide"
)
 
# Dashboard title
st.title("AI Excel Dashboard")
 
st.write(
    "Upload your Excel or CSV files "
    "to analyze your business data."
)
 
# Sidebar
st.sidebar.title("Navigation")
st.sidebar.info("Your business analytics dashboard")
 
# File uploader
st.header("Upload your dataset")
 
uploaded_file = st.file_uploader(
    "Choose an Excel or CSV file",
    type=["csv", "xlsx"],
    key="main_dataset_uploader"
)
 
# Read uploaded file
if uploaded_file is not None:
 
    try:
        df = read_file(uploaded_file)
 
        st.success("File uploaded and read successfully!")
        st.dataframe(df)
 
        # Data validation
        st.subheader("Data Validation")
 
        validation_report = validate_dataset(df)
 
        # Missing columns
        if validation_report["missing_columns"]:
            st.error(
                f"Missing columns: {validation_report['missing_columns']}"
            )
        else:
            st.success("All required columns are present.")
 
        # Missing values
        if not validation_report["missing_values"].empty:
            st.warning("Missing values detected:")
            st.write(validation_report["missing_values"])
        else:
            st.success("No missing values detected.")
 
        # Duplicate orders
        duplicates = validation_report["duplicate_orders"]
 
        if duplicates is not None and not duplicates.empty:
            st.warning("Duplicate orders detected:")
            st.dataframe(duplicates)
        else:
            st.success("No duplicate orders detected.")
 
        # Invalid data types
        if validation_report["invalid_data_types"]:
            st.warning(
                f"Invalid data types: {validation_report['invalid_data_types']}"
            )
        else:
            st.success("All data types are valid.")
 
        # Invalid business values
        for check_name, invalid_rows in validation_report[
            "invalid_business_values"
        ].items():
            if not invalid_rows.empty:
                st.warning(f"{check_name}: {len(invalid_rows)} invalid rows")
                st.dataframe(invalid_rows)
            else:
                st.success(f"{check_name}: No problems detected.")
 
    except Exception as e:
        st.error(f"Error reading or validating file: {e}")
 
    # Dataset information
    if "df" in locals():
        col1, col2 = st.columns(2)
 
        with col1:
            st.metric("Total Rows", len(df))
 
        with col2:
            st.metric("Total Columns", len(df.columns))
 
        # Data cleaning
        st.subheader("Data Cleaning")
 
        missing_strategy = st.selectbox(
            "How should missing values be handled?",
            options=["keep", "drop"],
            format_func=lambda x: (
                "Keep missing values" if x == "keep"
                else "Drop rows with missing values"
            )
        )
 
        if st.button("Clean Dataset"):
            cleaned_df = clean_dataset(
                df,
                missing_strategy=missing_strategy
            )
 
            st.session_state["cleaned_df"] = cleaned_df
 
        if "cleaned_df" in st.session_state:
            cleaned_df = st.session_state["cleaned_df"]
 
            st.success("Dataset cleaning completed!")
 
            col1, col2 = st.columns(2)
 
            with col1:
                st.metric("Original Rows", len(df))
 
            with col2:
                st.metric("Cleaned Rows", len(cleaned_df))
 
            st.subheader("Cleaned Dataset Preview")
            st.dataframe(cleaned_df)
 
            csv_data = cleaned_df.to_csv(index=False).encode("utf-8")
 
            st.download_button(
                label="Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv"
            )
 
# AI Business Insights section
    if "df" in locals():
        st.divider()
        st.header("AI Business Insights")
 
        # AI insights button - only show after data is loaded
        if st.button("Generate AI Insights", key="generate_ai_insights_btn"):
            with st.spinner("Generating AI insights..."):
                try:
                    analytics = {
                        "kpis": {
                            "total_revenue": df["Revenue"].sum() if "Revenue" in df.columns else 0,
                            "total_orders": df["Order_ID"].nunique() if "Order_ID" in df.columns else 0,
                            "units_sold": df["Quantity"].sum() if "Quantity" in df.columns else 0,
                            "average_order_value": (
                                df["Revenue"].sum() / df["Order_ID"].nunique()
                                if "Revenue" in df.columns and "Order_ID" in df.columns
                                else 0
                            ),
                        },
                        "products": {
                            "revenue_by_product": (
                                df.groupby("Product")["Revenue"]
                                .sum()
                                .to_dict()
                                if "Product" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                            "units_sold_by_product": (
                                df.groupby("Product")["Quantity"]
                                .sum()
                                .to_dict()
                                if "Product" in df.columns and "Quantity" in df.columns
                                else {}
                            ),
                            "revenue_by_category": (
                                df.groupby("Category")["Revenue"]
                                .sum()
                                .to_dict()
                                if "Category" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                        },
                        "time": {
                            "revenue_by_month": (
                                df.groupby(df["Date"].dt.month)["Revenue"]
                                .sum()
                                .to_dict()
                                if "Date" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                            "revenue_by_day": (
                                df.groupby(df["Date"].dt.day)["Revenue"]
                                .sum()
                                .to_dict()
                                if "Date" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                            "revenue_by_year": (
                                df.groupby(df["Date"].dt.year)["Revenue"]
                                .sum()
                                .to_dict()
                                if "Date" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                        },
                        "regions": {
                            "revenue_by_region": (
                                df.groupby("Region")["Revenue"]
                                .sum()
                                .to_dict()
                                if "Region" in df.columns and "Revenue" in df.columns
                                else {}
                            ),
                            "orders_by_region": (
                                df.groupby("Region")["Order_ID"]
                                .nunique()
                                .to_dict()
                                if "Region" in df.columns and "Order_ID" in df.columns
                                else {}
                            ),
                            "average_order_value_by_region": (
                                df.groupby("Region")
                                .apply(
                                    lambda x: x["Revenue"].sum() / x["Order_ID"].nunique()
                                    if "Revenue" in x.columns and "Order_ID" in x.columns
                                    else 0
                                )
                                .to_dict()
                                if "Region" in df.columns and "Revenue" in df.columns and "Order_ID" in df.columns
                                else {}
                            ),
                        },
                    }
 
                    result = generate_business_insights(analytics)
                    insights = result["insights"]
 
                    # Show validation problems instead of hiding the whole report
                    if not result["structure_valid"]:
                        st.warning("The AI response had some issues, but it is shown below.")
                        with st.expander("Validation issues"):
                            for issue in result["validation_issues"]:
                                st.write(f"- {issue}")
 
                    if not isinstance(insights, dict):
                        st.error("The AI did not return a usable report. Please try again.")
                    else:
                        # Executive summary
                        st.subheader("Executive summary")
                        es = insights.get("executive_summary")
                        st.write(es.get("text", "") if isinstance(es, dict) else "No summary generated.")
 
                        # Key observations
                        st.subheader("Key observations")
                        observations = insights.get("key_performance_observations", [])
                        if observations:
                            for obs in observations:
                                st.markdown(f"- **{obs.get('category', '')}**: {obs.get('analysis', '')}")
                        else:
                            st.write("No significant observations identified.")
 
                        # Business recommendations
                        st.subheader("Business recommendations")
                        recommendations = insights.get("business_recommendations", [])
                        if recommendations:
                            for rec in recommendations:
                                st.markdown(f"- **Action**: {rec.get('action', '')}")
                                st.caption(f"Reason: {rec.get('reason', '')}")
                                st.caption(f"Evidence: {', '.join(rec.get('evidence', []))}")
                                st.caption(f"Caveat: {rec.get('caveat', '')}")
                        else:
                            st.write("No recommendations at this time.")
 
                        # Data quality interpretation
                        st.subheader("Data quality interpretation")
                        dqi_items = insights.get("data_quality_interpretation", [])
                        if dqi_items:
                            for dqi in dqi_items:
                                st.markdown(f"- **{dqi.get('title', '')}**: {dqi.get('explanation', '')}")
                        else:
                            st.write("No data quality issues identified.")
 
                        # Further analysis opportunities
                        st.subheader("Further analysis opportunities")
                        fao = insights.get("further_analysis_opportunities", [])
                        if fao:
                            for item in fao:
                                st.markdown(
                                    f"- **{item.get('question', '')}** "
                                    f"(needs: {item.get('additional_data_required', '')})"
                                )
                        else:
                            st.write("No further analysis suggestions.")
 
                        # Limitations
                        limitations = insights.get("analysis_limitations", [])
                        if limitations:
                            st.subheader("Analysis limitations")
                            for limitation in limitations:
                                st.markdown(f"- {limitation}")
 
                except Exception as e:
                    st.error(f"Error generating AI insights: {e}")