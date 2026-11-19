"""Reading, cleaning, column-role detection and analytics for ANY dataset.

Nothing in this module depends on specific column names. The app guesses what
each column is (a number to measure, a category to group by, a date...) and the
user can correct the guesses before the analysis runs.
"""

import io
import re
import warnings
import zipfile

import pandas as pd

from src.security import upload_guard as _guard

ROLES = ["measure", "dimension", "date", "id", "text", "ignore"]

# Limits that keep a free, shared test server from running out of memory.
# One place decides the numbers: src/security/upload_guard.py (or the MAX_ROWS /
# MAX_COLUMNS environment variables), so every page and check agrees.
MAX_ROWS = _guard.MAX_ROWS
MAX_COLUMNS = _guard.MAX_COLUMNS
MAX_UNCOMPRESSED_BYTES = 200 * 1024 * 1024   # size of an Excel file once unpacked
_MAX_PACK_RATIO = 200                        # unpacked / packed, for big files only

MAX_MEASURES = 4      # numeric columns summarised in detail
MAX_DIMENSIONS = 4    # grouping columns compared against the main metric
TOP_N = 5             # groups kept per comparison (keeps the AI prompt small)

_NULL_TOKENS = {"", "nan", "none", "null", "n/a"}
_ID_TOKENS = {"id", "uuid", "guid", "sku", "code", "zip", "postal", "phone", "key"}
_CALENDAR_NAMES = {"year", "month", "day", "week", "quarter"}
_METRIC_HINTS = [
    "revenue", "sales", "amount", "total", "profit", "income",
    "salary", "price", "cost", "value", "quantity", "units",
]


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def _check_excel_archive(file_bytes):
    """Refuse files that are not real Excel files or that unpack to something huge."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            entries = archive.infolist()
    except zipfile.BadZipFile as error:
        raise ValueError("This does not look like a valid Excel (.xlsx) file.") from error

    unpacked = sum(entry.file_size for entry in entries)
    packed = sum(entry.compress_size for entry in entries) or 1
    too_big = unpacked > MAX_UNCOMPRESSED_BYTES
    suspicious = unpacked > 20 * 1024 * 1024 and unpacked / packed > _MAX_PACK_RATIO
    if too_big or suspicious:
        raise ValueError(
            "This Excel file is too large or unusual to open safely in the free test version. "
            "Try saving it again with fewer rows, or without images."
        )


def _enforce_limits(df):
    if len(df) > MAX_ROWS:
        raise ValueError(
            f"This file has more than {MAX_ROWS:,} rows. The free test version handles up to "
            f"{MAX_ROWS:,} rows. Please upload a smaller file, for example one period at a time."
        )
    if df.shape[1] > MAX_COLUMNS:
        raise ValueError(
            f"This file has more than {MAX_COLUMNS} columns. The free test version handles up to "
            f"{MAX_COLUMNS} columns."
        )
    return df


def list_sheets(file_bytes):
    """Return the sheet names of an Excel file."""
    _check_excel_archive(file_bytes)
    with pd.ExcelFile(io.BytesIO(file_bytes)) as workbook:
        return list(workbook.sheet_names)


def read_any_file(file_bytes, filename, sheet_name=None, header_row=0):
    """Read a CSV or Excel file into a DataFrame without assuming any columns.

    Reading stops one row after the limit, so an oversized file is refused without
    loading all of it into memory.
    """
    name = filename.lower()

    if name.endswith(".csv"):
        last_error = None
        for encoding in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(
                    io.BytesIO(file_bytes),
                    sep=None,            # detect the delimiter (, ; tab |)
                    engine="python",
                    encoding=encoding,
                    header=header_row,
                    nrows=MAX_ROWS + 1,
                )
                return _enforce_limits(df)
            except UnicodeDecodeError as error:
                last_error = error
        raise ValueError(f"Could not decode the CSV file: {last_error}")

    if name.endswith((".xlsx", ".xlsm")):
        _check_excel_archive(file_bytes)
        df = pd.read_excel(
            io.BytesIO(file_bytes),
            sheet_name=sheet_name if sheet_name is not None else 0,
            header=header_row,
            nrows=MAX_ROWS + 1,
        )
        return _enforce_limits(df)

    raise ValueError("Unsupported file type. Use .csv, .xlsx or .xlsm.")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _is_text_like(series):
    return not (
        pd.api.types.is_bool_dtype(series)
        or pd.api.types.is_numeric_dtype(series)
        or pd.api.types.is_datetime64_any_dtype(series)
    )


def _looks_like_id_name(name):
    text = str(name)
    tokens = set(re.split(r"[^a-z0-9]+", text.lower()))
    if tokens & _ID_TOKENS:
        return True
    return bool(re.search(r"[a-z]ID$|[a-z]Id$", text))


def _to_datetime(series, dayfirst=False):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            return pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=dayfirst)
        except (TypeError, ValueError):
            return pd.to_datetime(series, errors="coerce", dayfirst=dayfirst)


def _detect_dayfirst(sample):
    """Look at dates such as 05/01/2021 and decide if the day comes first.

    Returns (dayfirst, ambiguous). A value like 25/01/2021 proves day-first and
    01/25/2021 proves month-first. If every value could be read both ways the
    result is ambiguous and day-first is assumed (the common order outside the US).
    """
    parts = sample.astype(str).str.extract(r"^\s*(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})")
    first = pd.to_numeric(parts[0], errors="coerce")
    second = pd.to_numeric(parts[1], errors="coerce")
    if (first > 12).any():
        return True, False
    if (second > 12).any():
        return False, False
    if first.notna().any():
        return True, True
    return False, False   # no day/month/year-style dates (for example ISO dates)


def _ensure_datetime(series):
    if pd.api.types.is_datetime64_any_dtype(series):
        return series
    dayfirst, _ = _detect_dayfirst(series.dropna().head(200))
    return _to_datetime(series, dayfirst=dayfirst)


def _text_to_numbers(series):
    """Turn text such as '$1,200', '15%' or '(300)' into numbers."""
    text = series.astype("string").str.strip()
    text = text.str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    text = text.str.replace(r"[\s$€£¥%]", "", regex=True)

    # 1.234,50 (decimal comma) versus 1,234.50 (decimal point)
    sample = text.dropna().head(500)
    european = sample.str.fullmatch(
        r"[+-]?\d{1,3}(?:\.\d{3})+(?:,\d+)?|[+-]?\d+,\d{1,2}"
    ).sum()
    american = sample.str.fullmatch(
        r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+-]?\d+\.\d+"
    ).sum()
    if european > american:
        text = text.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    else:
        text = text.str.replace(",", "", regex=False)

    return pd.to_numeric(text, errors="coerce").astype("float64")


def _parse_dates_if_mostly_dates(series, date_order="auto"):
    """Convert text to dates if most values look like dates.

    Returns (dates, ambiguous) or None when the column is not a date column.
    date_order: "auto", "day_first" (31/12/2024) or "month_first" (12/31/2024).
    """
    sample = series.dropna().astype(str).head(200)
    if sample.empty:
        return None

    # Plain numbers such as 2024 or 20240315 are not treated as dates.
    looks_numeric = sample.str.fullmatch(r"[+-]?\d+(?:[.,]\d+)*")
    if looks_numeric.mean() > 0.8:
        return None

    if date_order == "day_first":
        dayfirst, ambiguous = True, False
    elif date_order == "month_first":
        dayfirst, ambiguous = False, False
    else:
        dayfirst, ambiguous = _detect_dayfirst(sample)

    if _to_datetime(sample, dayfirst=dayfirst).notna().mean() < 0.8:
        return None

    return _to_datetime(series, dayfirst=dayfirst), ambiguous


def _unique_headers(columns):
    headers, seen = [], {}
    for position, column in enumerate(columns, start=1):
        name = re.sub(r"\s+", " ", str(column)).strip()
        if not name or name.lower().startswith("unnamed:"):
            name = f"Column_{position}"
        count = seen.get(name, 0)
        seen[name] = count + 1
        headers.append(name if count == 0 else f"{name}_{count + 1}")
    return headers


def _num(value):
    """Round to 2 decimals and use plain ints for whole numbers (JSON-safe)."""
    if value is None or pd.isna(value):
        return None
    value = round(float(value), 2)
    if value in (float("inf"), float("-inf")):
        return None
    return int(value) if value.is_integer() else value


# --------------------------------------------------------------------------
# Safe exports and personal data
# --------------------------------------------------------------------------

_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _neutralize_cell(value):
    """Stop a text cell from running as a formula when the CSV is opened in Excel."""
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def to_safe_csv_bytes(df):
    """CSV bytes (UTF-8 with BOM, so accents open correctly in Excel) with formulas disarmed.

    Numbers and dates are untouched. Text cells and headers that start with = + - or @
    get a leading apostrophe, the standard way to keep spreadsheets from running them.
    """
    out = df.copy()
    out.columns = [_neutralize_cell(str(column)) for column in out.columns]
    for column in out.columns:
        series = out[column]
        if _is_text_like(series):
            out[column] = series.astype(object).map(_neutralize_cell)
    return out.to_csv(index=False).encode("utf-8-sig")


_PERSONAL_TOKENS = {
    "email", "mail", "correo", "phone", "telefono", "teléfono", "celular", "mobile",
    "address", "direccion", "dirección", "ssn", "passport", "pasaporte", "cedula",
    "cédula", "dni", "apellido", "surname", "birthday", "birthdate", "dob", "nacimiento",
}
_PERSONAL_PHRASES = ("first name", "last name", "full name", "customer name", "client name", "nombre")
_PERSON_WORDS = {"customer", "client", "cliente", "buyer", "comprador"}
_EMAIL_PATTERN = r"[^@\s]+@[^@\s]+\.[^@\s]+"
_PHONE_PATTERN = r"\+?[\d\s().-]{7,20}"
_DATE_LOOK = r"\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}.*"


def find_personal_columns(df):
    """Columns that look like they hold personal data. Returns {column: reason}."""
    found = {}
    for column in df.columns:
        name = re.sub(r"[^a-z0-9áéíóúñü]+", " ", str(column).lower()).strip()
        tokens = set(name.split())
        series = df[column]
        text_like = _is_text_like(series)
        sample = series.dropna().astype(str).str.strip().head(200) if text_like else None

        reason = None
        if tokens & _PERSONAL_TOKENS or any(phrase in name for phrase in _PERSONAL_PHRASES):
            reason = "the column name suggests personal data"
        elif text_like and tokens & _PERSON_WORDS:
            non_null = series.dropna()
            if len(non_null) and non_null.nunique() >= 10 and non_null.nunique() / len(non_null) >= 0.3:
                reason = "it looks like a list of customers"
        if reason is None and text_like and sample is not None and len(sample) >= 3:
            if sample.str.fullmatch(_EMAIL_PATTERN).mean() >= 0.5:
                reason = "many values look like email addresses"
            else:
                phone_like = (
                    sample.str.fullmatch(_PHONE_PATTERN)
                    & (sample.str.count(r"\d") >= 7)
                    & sample.str.contains(r"[+\-\s()]")
                    & ~sample.str.fullmatch(_DATE_LOOK)
                )
                if phone_like.mean() >= 0.6:
                    reason = "many values look like phone numbers"
        if reason:
            found[column] = reason
    return found


# --------------------------------------------------------------------------
# Cleaning
# --------------------------------------------------------------------------

def clean_dataset(
    df,
    remove_duplicates=True,
    convert_numbers=True,
    parse_dates=True,
    missing_strategy="keep",
    date_order="auto",
):
    """Clean any DataFrame. Returns (cleaned_df, list_of_actions_taken)."""
    report = []
    out = df.copy()
    out.columns = _unique_headers(out.columns)

    # Trim text and turn empty-like values into real missing values.
    for column in out.columns:
        if _is_text_like(out[column]):
            text = out[column].astype("string").str.strip()
            is_null = text.str.lower().isin(_NULL_TOKENS).fillna(False).astype(bool)
            out[column] = text.mask(is_null)

    # Drop columns and rows that are completely empty.
    columns_before, rows_before = out.shape[1], out.shape[0]
    out = out.dropna(axis=1, how="all").dropna(axis=0, how="all")
    if out.shape[1] < columns_before:
        report.append(f"Removed {columns_before - out.shape[1]} completely empty column(s).")
    if out.shape[0] < rows_before:
        report.append(f"Removed {rows_before - out.shape[0]} completely empty row(s).")

    # Convert text columns that are really numbers or dates.
    numeric_columns, date_columns, ambiguous_date_columns = [], [], []
    for column in list(out.columns):
        series = out[column]
        if not _is_text_like(series):
            continue

        if convert_numbers and not _looks_like_id_name(column):
            non_null = int(series.notna().sum())
            if non_null:
                leading_zero = (
                    series.astype("string").str.match(r"^0\d", na=False).sum() / non_null
                )
                numbers = _text_to_numbers(series)
                if leading_zero <= 0.1 and numbers.notna().sum() / non_null >= 0.9:
                    out[column] = numbers
                    numeric_columns.append(column)
                    continue

        if parse_dates:
            parsed = _parse_dates_if_mostly_dates(series, date_order)
            if parsed is not None:
                out[column], ambiguous = parsed
                date_columns.append(column)
                if ambiguous:
                    ambiguous_date_columns.append(column)

    if numeric_columns:
        report.append("Converted text to numbers in: " + ", ".join(numeric_columns) + ".")
    if date_columns:
        report.append("Converted text to dates in: " + ", ".join(date_columns) + ".")
    if ambiguous_date_columns:
        report.append(
            "Dates in " + ", ".join(ambiguous_date_columns) + " could be read as "
            "day/month or month/day; day/month was assumed. Change 'Order of day "
            "and month' above if that is wrong."
        )

    if remove_duplicates:
        before = len(out)
        out = out.drop_duplicates()
        if len(out) < before:
            report.append(f"Removed {before - len(out)} duplicate row(s).")

    missing_cells = int(out.isna().sum().sum())
    if missing_strategy == "drop" and missing_cells:
        before = len(out)
        out = out.dropna()
        report.append(f"Dropped {before - len(out)} row(s) that had missing values.")
    elif missing_strategy == "fill" and missing_cells:
        for column in out.columns:
            if not out[column].isna().any():
                continue
            if pd.api.types.is_bool_dtype(out[column]):
                continue
            if pd.api.types.is_numeric_dtype(out[column]):
                out[column] = out[column].fillna(out[column].median())
            elif _is_text_like(out[column]):
                out[column] = out[column].fillna("Unknown")
        report.append(
            "Filled missing values (median for numbers, 'Unknown' for text; "
            "dates were left as they are)."
        )
    elif missing_cells:
        report.append(f"Kept {missing_cells} missing value(s) as they are.")

    if not report:
        report.append("No cleaning was needed.")

    return out.reset_index(drop=True), report


# --------------------------------------------------------------------------
# Column roles
# --------------------------------------------------------------------------

def infer_column_roles(df):
    """Guess a role for every column: measure, dimension, date, id, text or ignore."""
    roles = {}

    for column in df.columns:
        series = df[column]
        non_null = series.dropna()
        count = len(non_null)
        unique = int(non_null.nunique()) if count else 0

        if count == 0 or unique <= 1:
            roles[column] = "ignore"
        elif pd.api.types.is_datetime64_any_dtype(series):
            roles[column] = "date"
        elif pd.api.types.is_bool_dtype(series):
            roles[column] = "dimension"
        elif pd.api.types.is_numeric_dtype(series):
            if _looks_like_id_name(column) and unique >= 0.9 * count:
                roles[column] = "id"
            elif str(column).strip().lower() in _CALENDAR_NAMES:
                roles[column] = "dimension"
            else:
                roles[column] = "measure"
        else:
            if _looks_like_id_name(column) and unique >= 0.9 * count:
                roles[column] = "id"
            elif unique <= 50 and (unique <= 0.5 * count or unique <= 12):
                roles[column] = "dimension"
            else:
                roles[column] = "text"

    return roles


def suggest_main_measure(df, roles):
    measures = [c for c in df.columns if roles.get(c) == "measure"]
    if not measures:
        return None
    for hint in _METRIC_HINTS:
        for column in measures:
            if hint in str(column).lower():
                return column
    return measures[0]


def suggest_main_date(df, roles):
    dates = [c for c in df.columns if roles.get(c) == "date"]
    if not dates:
        return None
    for column in dates:
        if "date" in str(column).lower():
            return column
    return dates[0]


# --------------------------------------------------------------------------
# Aggregation helpers (also used by the charts)
# --------------------------------------------------------------------------

def aggregate_by_group(df, dimension, measure, aggregation="sum"):
    """Aggregate a measure by the values of a dimension, largest first."""
    values = pd.to_numeric(df[measure], errors="coerce")
    grouped = values.groupby(df[dimension]).agg(aggregation)
    return grouped.dropna().sort_values(ascending=False)


def aggregate_by_period(df, date_column, measure, aggregation="sum", freq="M"):
    """Aggregate by year ('Y'), month ('M') or day ('D'). Counts rows if no measure."""
    dates = _ensure_datetime(df[date_column])
    valid = dates.notna()
    if not valid.any():
        return pd.Series(dtype="float64")

    valid_dates = dates[valid]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if freq == "Y":
            keys = valid_dates.dt.year.astype(str)
        elif freq == "M":
            keys = valid_dates.dt.to_period("M").astype(str)
        else:
            keys = valid_dates.dt.strftime("%Y-%m-%d")

    if measure:
        values = pd.to_numeric(df.loc[valid, measure], errors="coerce")
        result = values.groupby(keys).agg(aggregation)
    else:
        result = keys.groupby(keys).size()

    return result.dropna().sort_index()


# --------------------------------------------------------------------------
# Analytics (the facts the AI will interpret)
# --------------------------------------------------------------------------

def build_generic_analytics(
    df,
    roles,
    main_measure=None,
    main_date=None,
    dimensions=None,
    aggregation="sum",
):
    """Build a compact dictionary of facts about any dataset."""
    work = df.reset_index(drop=True)

    measures = [c for c in work.columns if roles.get(c) == "measure"]
    if main_measure in measures:
        measures.remove(main_measure)
        measures.insert(0, main_measure)
    else:
        main_measure = None
    measures = measures[:MAX_MEASURES]

    if dimensions is None:
        dimensions = sorted(
            [c for c in work.columns if roles.get(c) == "dimension"],
            key=lambda c: work[c].nunique(),
        )
    dimensions = [c for c in dimensions if c in work.columns][:MAX_DIMENSIONS]

    if main_date not in work.columns:
        main_date = None

    analytics = {}

    # ---- overview
    analytics["overview"] = {
        "rows": int(len(work)),
        "columns": int(work.shape[1]),
        "settings": {
            "main_metric": main_measure or "none (record counts only)",
            "aggregation_used": aggregation,
            "date_column": main_date or "none",
        },
        "column_names": {
            "measure_columns": ", ".join(measures) or "none",
            "group_columns": ", ".join(dimensions) or "none",
        },
    }

    # ---- measure statistics
    stats = {}
    for measure in measures:
        values = pd.to_numeric(work[measure], errors="coerce").dropna()
        if values.empty:
            continue
        stats[measure] = {
            "total": _num(values.sum()),
            "average": _num(values.mean()),
            "median": _num(values.median()),
            "minimum": _num(values.min()),
            "maximum": _num(values.max()),
            "records_with_value": int(values.size),
        }
    analytics["measures"] = stats

    # ---- comparison by group
    by_group = {}
    for dimension in dimensions:
        info = {"distinct_groups": int(work[dimension].nunique())}
        counts = work[dimension].value_counts().head(TOP_N)
        info["records_per_group"] = {str(k): int(v) for k, v in counts.items()}

        if main_measure:
            grouped = aggregate_by_group(work, dimension, main_measure, aggregation)
            if not grouped.empty:
                info["top_groups"] = {str(k): _num(v) for k, v in grouped.head(TOP_N).items()}
                if len(grouped) > TOP_N:
                    info["lowest_groups"] = {str(k): _num(v) for k, v in grouped.tail(2).items()}
                info["top_group"] = str(grouped.index[0])
                if aggregation == "sum" and not (grouped < 0).any() and grouped.sum() > 0:
                    info["top_group_share_of_total_pct"] = _num(
                        grouped.iloc[0] / grouped.sum() * 100
                    )
        by_group[dimension] = info
    analytics["by_group"] = by_group

    # ---- time
    if main_date:
        dates = _ensure_datetime(work[main_date])
        valid = dates.dropna()
        if not valid.empty:
            span_days = int((valid.max() - valid.min()).days)
            time_info = {
                "first_date": valid.min().strftime("%Y-%m-%d"),
                "last_date": valid.max().strftime("%Y-%m-%d"),
                "records_without_valid_date": int(dates.isna().sum()),
                "values_are": main_measure or "record counts",
            }

            if span_days >= 60:
                by_year = aggregate_by_period(work, main_date, main_measure, aggregation, "Y")
                if len(by_year) >= 2:
                    time_info["by_year"] = {str(k): _num(v) for k, v in by_year.tail(10).items()}

                by_month = aggregate_by_period(work, main_date, main_measure, aggregation, "M")
                if not by_month.empty:
                    time_info["by_month"] = {str(k): _num(v) for k, v in by_month.tail(12).items()}
                    time_info["peak_month"] = str(by_month.idxmax())
                    time_info["peak_month_value"] = _num(by_month.max())
                    time_info["lowest_month"] = str(by_month.idxmin())
                    time_info["lowest_month_value"] = _num(by_month.min())
                    if len(by_month) >= 2 and by_month.iloc[-2] != 0:
                        time_info["latest_month_change_vs_previous_pct"] = _num(
                            (by_month.iloc[-1] - by_month.iloc[-2])
                            / abs(by_month.iloc[-2]) * 100
                        )
            else:
                by_day = aggregate_by_period(work, main_date, main_measure, aggregation, "D")
                if not by_day.empty:
                    time_info["by_day"] = {str(k): _num(v) for k, v in by_day.tail(14).items()}

            analytics["time"] = time_info

    # ---- relationships between numeric columns
    all_measures = [c for c in work.columns if roles.get(c) == "measure"][:8]
    if len(all_measures) >= 2 and len(work) >= 10:
        numeric = work[all_measures].apply(pd.to_numeric, errors="coerce")
        corr = numeric.corr()
        pairs = []
        for i, first in enumerate(all_measures):
            for second in all_measures[i + 1:]:
                value = corr.loc[first, second]
                if pd.notna(value):
                    pairs.append((abs(value), first, second, value))
        pairs.sort(reverse=True)
        if pairs:
            analytics["relationships"] = {
                f"{first} vs {second}": round(float(value), 2)
                for _, first, second, value in pairs[:3]
            }

    # ---- data quality
    missing = (work.isna().mean() * 100).round(2)
    missing = missing[missing > 0].sort_values(ascending=False)
    quality = {
        "duplicate_rows": int(work.duplicated().sum()),
        "columns_with_missing_values_count": int(len(missing)),
        "highest_missing_columns_pct": {str(k): float(v) for k, v in missing.head(5).items()},
    }

    outliers = {}
    for measure in measures:
        values = pd.to_numeric(work[measure], errors="coerce").dropna()
        if len(values) < 8:
            continue
        q1, q3 = values.quantile([0.25, 0.75])
        spread = q3 - q1
        count = int(((values < q1 - 1.5 * spread) | (values > q3 + 1.5 * spread)).sum())
        if count:
            outliers[measure] = count
    quality["outlier_counts"] = outliers

    if main_measure:
        negatives = int((pd.to_numeric(work[main_measure], errors="coerce") < 0).sum())
        quality["negative_values_in_main_metric"] = negatives

    analytics["data_quality"] = quality

    return analytics
