
import streamlit as st

from src.data.data_reader import read_file
from src.data.data_validator import validate_dataset
from src.data.data_cleaner import clean_dataset

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
