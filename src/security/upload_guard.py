"""Safety checks for files uploaded to a public demo.

Pure Python (no Streamlit), so every rule can be tested on its own.

What is covered:
- Limits on file size, spreadsheet size, rows and columns, so one big or booby-trapped
  file cannot use up the free server (an .xlsx is a zip file and can unpack to huge sizes).
- Download files that cannot run formulas when opened in Excel ("formula injection").
- Detection of columns that look like personal data (emails, phones, addresses, names...).
- Cleaning of text that is put into the AI prompt, so a product name cannot smuggle in
  extra instruction lines.
"""

import io
import os
import re
import unicodedata
import zipfile

import pandas as pd


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# Limits for the free demo. Change them with environment variables if needed.
MAX_FILE_MB = _env_int("MAX_FILE_MB", 25)
MAX_UNCOMPRESSED_MB = _env_int("MAX_UNCOMPRESSED_MB", 200)
MAX_ROWS = _env_int("MAX_ROWS", 100_000)
MAX_COLUMNS = _env_int("MAX_COLUMNS", 100)
MAX_ZIP_ENTRIES = 2000

_MB = 1024 * 1024


class UploadRejected(ValueError):
    """The file is refused. The message is written to be shown to the visitor."""


# --------------------------------------------------------------------------
# 1. Limits
# --------------------------------------------------------------------------

def check_file_bytes(data, filename, max_file_mb=None, max_uncompressed_mb=None):
    """Reject files that are too big, or Excel files that unpack to something huge."""
    max_file_mb = MAX_FILE_MB if max_file_mb is None else max_file_mb
    max_uncompressed_mb = MAX_UNCOMPRESSED_MB if max_uncompressed_mb is None else max_uncompressed_mb

    if len(data) > max_file_mb * _MB:
        raise UploadRejected(
            f"This file is {len(data) / _MB:.1f} MB. The free test version accepts files up to "
            f"{max_file_mb} MB. Try a smaller export or fewer columns."
        )

    if filename.lower().endswith((".xlsx", ".xlsm")):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                entries = archive.infolist()
        except zipfile.BadZipFile as error:
            raise UploadRejected(
                "This does not look like a valid Excel (.xlsx) file. "
                "Open it in Excel and use Save As to create a new .xlsx or .csv."
            ) from error

        if len(entries) > MAX_ZIP_ENTRIES:
            raise UploadRejected("This Excel file has an unusual structure and was not opened.")
        if sum(entry.file_size for entry in entries) > max_uncompressed_mb * _MB:
            raise UploadRejected(
                "This Excel file is far larger than it looks once opened, so it was not loaded. "
                "Try saving it again as a .csv."
            )


def check_sheet_size(data, filename, sheet_name=None, max_rows=None, max_columns=None):
    """Reject Excel sheets with too many rows or columns BEFORE pandas loads them."""
    if not filename.lower().endswith((".xlsx", ".xlsm")):
        return
    max_rows = MAX_ROWS if max_rows is None else max_rows
    max_columns = MAX_COLUMNS if max_columns is None else max_columns

    try:
        from openpyxl import load_workbook

        workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception:
        return  # cannot tell; the checks after loading still apply

    used_rows = used_cols = 0
    try:
        if isinstance(sheet_name, str) and sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
        else:
            index = sheet_name if isinstance(sheet_name, int) else 0
            sheet = workbook.worksheets[index]

        declared_rows, declared_cols = sheet.max_row or 0, sheet.max_column or 0
        if declared_rows <= max_rows + 1 and declared_cols <= max_columns:
            return

        # The declared size can be inflated by formatting (empty styled cells),
        # so count the cells that really hold data. Stop early once over the limit.
        for row in sheet.iter_rows(values_only=True):
            filled = [i for i, value in enumerate(row, 1) if value is not None and value != ""]
            if filled:
                used_rows += 1
                used_cols = max(used_cols, filled[-1])
                if used_rows > max_rows + 1:
                    break
    except Exception:
        return
    finally:
        workbook.close()

    if used_rows > max_rows + 1:
        raise UploadRejected(
            f"This sheet has more than {max_rows:,} rows. The free test version handles up to "
            f"{max_rows:,} rows. Filter the data or split it into smaller files."
        )
    if used_cols > max_columns:
        raise UploadRejected(
            f"This sheet has {used_cols:,} columns. The free test version handles up to {max_columns} columns."
        )


def check_frame(df, max_rows=None, max_columns=None):
    """Reject tables with too many rows or columns after loading."""
    max_rows = MAX_ROWS if max_rows is None else max_rows
    max_columns = MAX_COLUMNS if max_columns is None else max_columns
    if len(df) > max_rows:
        raise UploadRejected(
            f"This file has {len(df):,} rows. The free test version handles up to {max_rows:,} rows. "
            "Filter the data or split it into smaller files."
        )
    if df.shape[1] > max_columns:
        raise UploadRejected(
            f"This file has {df.shape[1]:,} columns. The free test version handles up to {max_columns} columns."
        )


# --------------------------------------------------------------------------
# 2. Downloads that cannot run formulas
# --------------------------------------------------------------------------

# Text that starts with = @ tab or return, or with + / - followed by something that
# is not a plain number, can be run as a formula when the file is opened in Excel.
_FORMULA_START = re.compile(r"^(?:[=@\t\r]|[+-](?=.)(?!\d[\d.,]*$))")


def neutralize_cell(value):
    """Prefix risky text with an apostrophe so spreadsheets show it as plain text."""
    if isinstance(value, str) and _FORMULA_START.match(value):
        return "'" + value
    return value


def safe_for_spreadsheet(df):
    """Copy of the table that is safe to open in Excel (headers and text cells)."""
    out = df.copy()
    out.columns = [neutralize_cell(str(column)) for column in out.columns]
    for column in out.columns:
        series = out[column]
        if series.dtype == object or pd.api.types.is_string_dtype(series):
            out[column] = series.map(neutralize_cell)
    return out


def to_safe_csv_bytes(df):
    """CSV bytes that are safe to open in Excel and keep accents (UTF-8 with BOM)."""
    return safe_for_spreadsheet(df).to_csv(index=False).encode("utf-8-sig")


# --------------------------------------------------------------------------
# 3. Personal data
# --------------------------------------------------------------------------

_NAME_WORDS = {"name", "names", "nombre", "nombres", "apellido", "apellidos", "surname"}
_PERSON_WORDS = {
    "customer", "client", "cliente", "user", "usuario", "employee", "empleado",
    "contact", "contacto", "buyer", "comprador", "first", "last", "full", "middle",
}
_STRONG = {
    "an email address": {"email", "emails", "correo", "correos", "mail"},
    "a phone number": {"phone", "telefono", "celular", "mobile", "cellphone", "whatsapp", "tel"},
    "an address": {"address", "direccion", "domicilio"},
    "an ID document": {"ssn", "passport", "pasaporte", "cedula", "dni", "curp", "nif"},
}
_PERSON_ONLY = {"customer", "client", "cliente", "usuario", "employee", "empleado"}
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _name_tokens(name):
    text = unicodedata.normalize("NFKD", str(name))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return set(re.split(r"[^a-z0-9]+", text.lower())) - {""}


def find_personal_columns(df):
    """Columns that look like personal data. Returns {column: short reason}."""
    found = {}
    for column in df.columns:
        tokens = _name_tokens(column)
        series = df[column]

        reason = next((why for why, words in _STRONG.items() if tokens & words), None)
        if reason is None and tokens & _NAME_WORDS and tokens & _PERSON_WORDS:
            reason = "a person's name"

        is_text = not (
            pd.api.types.is_numeric_dtype(series)
            or pd.api.types.is_datetime64_any_dtype(series)
            or pd.api.types.is_bool_dtype(series)
        )
        if reason is None and is_text:
            sample = series.dropna().astype(str).head(500)
            if len(sample):
                if sample.map(lambda v: bool(_EMAIL.match(v.strip()))).mean() >= 0.5:
                    reason = "an email address"
                elif tokens & _PERSON_ONLY and series.nunique() > 20 and series.nunique() / len(series.dropna()) > 0.3:
                    reason = "a person's name"

        if reason:
            found[column] = f"looks like {reason}"
    return found


# --------------------------------------------------------------------------
# 4. Text that goes into the AI prompt
# --------------------------------------------------------------------------

def sanitize_label(value, limit=80):
    """One short line of plain text: no line breaks or control characters, capped in length."""
    text = unicodedata.normalize("NFKC", str(value))
    text = "".join(
        " " if (unicodedata.category(ch)[0] in ("C", "Z") and ch != " ") else ch
        for ch in text
    )
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text
