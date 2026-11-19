"""Cached versions of the slow steps (reading and tidying a file).

Streamlit re-runs the whole page on every click. Without a cache, each click would read
and clean the file again. With it, the same file and the same settings are done once.
The cache is small and short-lived on purpose, so a shared free server keeps its memory.
"""

import streamlit as st

from src.generic import generic_analysis as ga


@st.cache_data(max_entries=2, ttl=900, show_spinner="Reading your file...")
def read_cached(file_bytes, filename, sheet_name=None, header_row=0):
    return ga.read_any_file(file_bytes, filename, sheet_name, header_row)


@st.cache_data(max_entries=2, ttl=900, show_spinner="Tidying your data...")
def clean_cached(
    df,
    remove_duplicates=True,
    convert_numbers=True,
    parse_dates=True,
    missing_strategy="keep",
    date_order="auto",
):
    return ga.clean_dataset(
        df,
        remove_duplicates=remove_duplicates,
        convert_numbers=convert_numbers,
        parse_dates=parse_dates,
        missing_strategy=missing_strategy,
        date_order=date_order,
    )
