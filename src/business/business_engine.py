"""Business analytics for people who never open Excel.

Works with any sales-style file: it guesses which column is the revenue, the
date, the product and so on (the user can correct it), then calculates the
numbers, compares the latest period with the one before, and raises alerts in
plain language. Everything here is plain pandas, so every number is exact. The
AI only explains these results.
"""

import re

import numpy as np
import pandas as pd

from src.generic import generic_analysis as ga
from src.i18n import is_spanish, t

# Fields the page understands. "revenue" is the money coming in.
FIELDS = ["revenue", "date", "product", "category", "region", "order_id", "quantity", "unit_price"]

FIELD_LABELS = {
    "revenue": "Money earned (revenue / sales)",
    "date": "Date",
    "product": "Product",
    "category": "Category",
    "region": "Region / store / city",
    "order_id": "Order number",
    "quantity": "Units sold (quantity)",
    "unit_price": "Price per unit",
}

# Which column types each field may use ("any" = no restriction).
_ALLOWED_ROLES = {
    "revenue": {"measure"},
    "quantity": {"measure"},
    "unit_price": {"measure"},
    "date": {"date"},
    "product": {"dimension", "text"},
    "category": {"dimension", "text"},
    "region": {"dimension", "text"},
    "order_id": {"id", "measure", "dimension", "text"},
}

# Name hints in English and Spanish, strongest first.
_HINTS = {
    "revenue": ["revenue", "sales", "ventas", "ingresos", "importe", "monto",
                "amount", "income", "total sales", "total"],
    "date": ["order date", "date", "fecha", "day", "dia", "día"],
    "product": ["product", "producto", "item", "articulo", "artículo", "sku"],
    "category": ["category", "categoria", "categoría", "segment", "department", "departamento"],
    "region": ["region", "región", "zone", "zona", "city", "ciudad", "country",
               "pais", "país", "state", "store", "tienda", "branch", "sucursal", "area"],
    "order_id": ["order id", "order number", "order", "pedido", "invoice", "factura",
                 "ticket", "transaction", "orden"],
    "quantity": ["quantity", "qty", "units", "cantidad", "unidades"],
    "unit_price": ["unit price", "price", "precio", "precio unitario"],
}

# Order matters: more specific fields claim their column first.
_ASSIGN_ORDER = ["date", "quantity", "unit_price", "order_id", "revenue", "product", "category", "region"]


# --------------------------------------------------------------------------
# Formatting helpers (plain language)
# --------------------------------------------------------------------------

def _local_separators(text):
    """Spanish style: 12.345,67 instead of 12,345.67."""
    if is_spanish():
        return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return text


def fmt_number(value):
    """Readable number: 12,345 or 12,345.67 (12.345,67 in Spanish). Missing values give 'n/a'."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return t("n/a")
    value = float(value)
    if abs(value) >= 100 or value == int(value):
        return _local_separators(f"{value:,.0f}")
    return _local_separators(f"{value:,.2f}")


def fmt_pct(value, signed=True):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return t("n/a")
    return _local_separators(f"{value:+.1f}%" if signed else f"{value:.1f}%")


_MONTHS_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def period_text(value, unit):
    """Short label for a chart point: a day, a week start, or a month."""
    stamp = pd.Timestamp(value)
    if unit == "month":
        return f"{_MONTHS_ES[stamp.month - 1]} {stamp.year}" if is_spanish() else stamp.strftime("%b %Y")
    return _date_text(stamp)


def _date_text(value):
    stamp = pd.Timestamp(value)
    if is_spanish():
        return f"{stamp.day} {_MONTHS_ES[stamp.month - 1]} {stamp.year}"
    return stamp.strftime("%b %d, %Y")


# --------------------------------------------------------------------------
# 1. Column matching
# --------------------------------------------------------------------------

def _norm(name):
    return re.sub(r"[^a-z0-9áéíóúñü]+", " ", str(name).lower()).strip()


def _name_score(column, hints):
    """0 = no match, 1 = partial, 2 = word match, 3 = exact."""
    name = _norm(column)
    words = set(name.split())
    best = 0
    for hint in hints:
        hint_norm = _norm(hint)
        hint_words = hint_norm.split()
        if name == hint_norm:
            best = max(best, 3)
        elif all(word in words for word in hint_words):
            best = max(best, 2)
        elif len(hint_norm) >= 4 and hint_norm in name:
            best = max(best, 1)
    return best


def guess_mapping(df, roles=None):
    """Guess which column plays which business role. Returns {field: column or None}."""
    roles = roles or ga.infer_column_roles(df)
    mapping = {field: None for field in FIELDS}
    used = set()

    for field in _ASSIGN_ORDER:
        best_column, best_score = None, 0
        for column in df.columns:
            if column in used:
                continue
            if roles.get(column, "text") not in _ALLOWED_ROLES[field]:
                continue
            score = _name_score(column, _HINTS[field])
            if score > best_score:
                best_column, best_score = column, score
        if best_column is not None:
            mapping[field] = best_column
            used.add(best_column)

    # Revenue fallback: the most "money-like" numeric column that is not an id.
    if mapping["revenue"] is None and not (mapping["quantity"] and mapping["unit_price"]):
        candidates = [
            c for c in df.columns
            if roles.get(c) == "measure" and c not in used and not ga._looks_like_id_name(c)
        ]
        if candidates:
            choice = ga.suggest_main_measure(df[candidates], {c: "measure" for c in candidates})
            mapping["revenue"] = choice

    if mapping["date"] is None:
        mapping["date"] = ga.suggest_main_date(df, roles)

    return mapping


# --------------------------------------------------------------------------
# 2. Standard frame
# --------------------------------------------------------------------------

def prepare_frame(df, mapping):
    """Build a frame with standard column names from the user's own columns.

    Returns (work, notes, metric_label). 'revenue' always exists in work: it is the
    mapped column, quantity x price if there is no revenue column, or 1 per row
    (then metric_label is "Records").
    """
    notes = []
    work = pd.DataFrame(index=df.index)

    for field in FIELDS:
        column = mapping.get(field)
        if column and column in df.columns:
            work[field] = df[column]

    for field in ("revenue", "quantity", "unit_price"):
        if field in work:
            work[field] = pd.to_numeric(work[field], errors="coerce")

    metric_label = "Revenue"
    if "revenue" not in work:
        if "quantity" in work and "unit_price" in work:
            work["revenue"] = work["quantity"] * work["unit_price"]
            notes.append(t("There is no revenue column, so revenue = units sold x price per unit."))
        else:
            work["revenue"] = 1.0
            metric_label = "Records"
            notes.append(
                t("No money column was found, so each row counts as one record. "
                  "Pick a revenue column above for money totals.")
            )

    if "date" in work:
        work["date"] = ga._ensure_datetime(work["date"])
        bad = int(work["date"].isna().sum())
        if bad:
            notes.append(t("{bad} row(s) have no usable date and are left out of trends.", bad=bad))

    for field in ("product", "category", "region", "order_id"):
        if field in work:
            work[field] = work[field].astype("string").str.strip()

    if "order_id" in work:
        duplicated = work.duplicated(keep="first")
        if duplicated.any():
            work = work[~duplicated]
            notes.append(t("Removed {count} exact duplicate row(s) (same order number and values).", count=int(duplicated.sum())))
    else:
        copies = int(work.duplicated().sum())
        if copies:
            notes.append(
                t("{copies} row(s) are identical to another row. They were kept because "
                  "there is no order number to prove they are duplicates.", copies=copies)
            )

    return work.reset_index(drop=True), notes, metric_label


# --------------------------------------------------------------------------
# 3. KPIs and period comparison
# --------------------------------------------------------------------------

def compute_kpis(work):
    revenue = float(work["revenue"].sum())
    if "order_id" in work:
        orders = int(work["order_id"].nunique())
    else:
        orders = int(len(work))
    kpis = {
        "revenue": revenue,
        "orders": orders,
        "average_order_value": revenue / orders if orders else None,
    }
    if "quantity" in work:
        kpis["units_sold"] = float(work["quantity"].sum())
    return kpis


def split_periods(work):
    """Latest period vs the one before it, anchored to the last date in the data.

    Uses the last 30 days when there are at least 60 days of data, otherwise splits
    the data in two equal halves (at least 7 days each). Returns None if impossible.
    """
    if "date" not in work:
        return None
    days = work["date"].dropna().dt.normalize()
    if days.empty:
        return None

    first, last = days.min(), days.max()
    span = int((last - first).days) + 1
    length = 30 if span >= 60 else span // 2
    if length < 7:
        return None

    current_start = last - pd.Timedelta(days=length - 1)
    previous_end = current_start - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=length - 1)

    all_days = work["date"].dt.normalize()
    current = work[(all_days >= current_start) & (all_days <= last)]
    previous = work[(all_days >= previous_start) & (all_days <= previous_end)]

    return {
        "length_days": length,
        "current": current,
        "previous": previous,
        "current_label": t("{start} to {end}", start=_date_text(current_start), end=_date_text(last)),
        "previous_label": t("{start} to {end}", start=_date_text(previous_start), end=_date_text(previous_end)),
    }


def _change_pct(current, previous):
    if previous is None or current is None or previous == 0:
        return None
    return (current - previous) / abs(previous) * 100


def compare_periods(periods):
    """KPIs for both periods and the percentage change of each."""
    current = compute_kpis(periods["current"])
    previous = compute_kpis(periods["previous"])
    changes = {key: _change_pct(current.get(key), previous.get(key)) for key in current}
    return {"current": current, "previous": previous, "change_pct": changes}


# --------------------------------------------------------------------------
# 4. Top lists and group movement
# --------------------------------------------------------------------------

def group_totals(work, field):
    """Revenue by group, largest first. Empty Series if the field is not mapped."""
    if field not in work:
        return pd.Series(dtype="float64")
    totals = work.groupby(field, dropna=True)["revenue"].sum()
    return totals.sort_values(ascending=False)


def group_movement(periods, field):
    """Revenue of each group in the latest vs the previous period."""
    current = group_totals(periods["current"], field)
    previous = group_totals(periods["previous"], field)
    table = pd.DataFrame({"current": current, "previous": previous}).fillna(0.0)
    previous_rows = periods["previous"].groupby(field, dropna=True).size()
    table["previous_rows"] = previous_rows.reindex(table.index).fillna(0).astype(int)
    table["change"] = table["current"] - table["previous"]
    table["change_pct"] = [
        _change_pct(c, p) if p > 0 else None for c, p in zip(table["current"], table["previous"])
    ]
    return table.sort_values("change")


# --------------------------------------------------------------------------
# 5. Alerts
# --------------------------------------------------------------------------

_SEVERITY_ORDER = {"high": 0, "medium": 1, "info": 2}


def _alert(severity, title, detail):
    return {"severity": severity, "title": title, "detail": detail}


def _daily_totals(work):
    if "date" not in work:
        return pd.Series(dtype="float64")
    valid = work.dropna(subset=["date"])
    return valid.groupby(valid["date"].dt.normalize())["revenue"].sum()


def build_alerts(work, periods=None, comparison=None, metric_label="Revenue", max_alerts=8):
    """Detect things an owner should look at. Every alert is plain text with exact numbers."""
    alerts = []
    disp = t(metric_label)       # "Revenue" -> "Ingresos" in Spanish
    label = disp.lower()
    days = periods["length_days"] if periods else 0
    names = {"metric_label": disp, "label": label, "days": days}

    # --- overall movement
    if comparison:
        change = comparison["change_pct"].get("revenue")
        if change is not None:
            current = comparison["current"]["revenue"]
            previous = comparison["previous"]["revenue"]
            lower_text = t("In the last {days} days, {label} was {current}, {pct} lower than the {days} days before ({previous}).",
                           **names, current=fmt_number(current), pct=fmt_pct(abs(change), signed=False), previous=fmt_number(previous))
            if change <= -30:
                alerts.append(_alert("high", t("{metric_label} fell sharply", **names), lower_text))
            elif change <= -15:
                alerts.append(_alert("medium", t("{metric_label} is going down", **names), lower_text))
            elif change >= 25:
                alerts.append(_alert("info", t("{metric_label} is growing strongly", **names),
                    t("In the last {days} days, {label} was {current}, {pct} higher than the {days} days before ({previous}).",
                      **names, current=fmt_number(current), pct=fmt_pct(change, signed=False), previous=fmt_number(previous))))

    # --- groups that stopped selling or dropped a lot
    if periods:
        previous_total = float(periods["previous"]["revenue"].sum())
        previous_rows_total = len(periods["previous"])
        overall = comparison["change_pct"].get("revenue") if comparison else None
        # When everything is falling, only flag groups that fall clearly more than the rest.
        fall_limit = -30.0 if overall is None or overall >= 0 else min(-30.0, overall - 15.0)
        group_drops = 0
        product_stopped = False
        for field, noun in (("product", "product"), ("region", "region"), ("category", "category")):
            if field not in work or previous_total <= 0 or previous_rows_total == 0:
                continue
            movement = group_movement(periods, field)
            # A group matters if it had a real share of the money OR of the sales records.
            relevant = movement[
                (movement["previous"] >= 0.05 * previous_total)
                | (movement["previous_rows"] >= 0.05 * previous_rows_total)
            ]

            stopped = relevant[relevant["current"] <= 0]
            # A category that stopped is usually the same news as its stopped product.
            if not stopped.empty and not (field == "category" and product_stopped):
                who_names = ", ".join(str(n) for n in stopped.index[:3])
                extra = t(" and {more} more", more=len(stopped) - 3) if len(stopped) > 3 else ""
                many = len(stopped) > 1
                if noun == "product":
                    detail = t("These products sold before but had no sales in the last {days} days.", **names) if many \
                        else t("This product sold before but had no sales in the last {days} days.", **names)
                elif noun == "region":
                    detail = t("These regions sold before but had no sales in the last {days} days.", **names) if many \
                        else t("This region sold before but had no sales in the last {days} days.", **names)
                else:
                    detail = t("These categories sold before but had no sales in the last {days} days.", **names) if many \
                        else t("This category sold before but had no sales in the last {days} days.", **names)
                alerts.append(_alert("high", t("No sales at all for: {names}{extra}", names=who_names, extra=extra), detail))
                if field == "product":
                    product_stopped = True

            fell = relevant[
                (relevant["current"] > 0)
                & (relevant["change_pct"].notna())
                & (relevant["change_pct"] <= fall_limit)
                & (relevant["previous"] >= 0.05 * previous_total)
            ]
            for name, row in fell.sort_values("change").head(1).iterrows():
                if group_drops >= 3:
                    break
                group_drops += 1
                if noun == "product":
                    drop_title = t("Product '{name}' dropped a lot", name=name)
                elif noun == "region":
                    drop_title = t("Region '{name}' dropped a lot", name=name)
                else:
                    drop_title = t("Category '{name}' dropped a lot", name=name)
                alerts.append(_alert("medium", drop_title,
                    t("{metric_label} went from {previous} to {current} ({pct}) compared with the previous {days} days.",
                      **names, previous=fmt_number(row['previous']), current=fmt_number(row['current']),
                      pct=fmt_pct(row['change_pct']))))

    # --- unusual days (robust to a few big days)
    daily = _daily_totals(work)
    if len(daily) >= 21:
        median = float(daily.median())
        mad = float((daily - median).abs().median())
        if mad > 0:
            scores = 0.6745 * (daily - median) / mad
            unusual = scores[scores.abs() > 3.5]
            unusual = unusual.reindex(unusual.abs().sort_values(ascending=False).index)
            for day in unusual.index[:3]:
                value = daily[day]
                severity = "info" if value > median else "medium"
                text_key = (
                    t("{metric_label} that day was {value}, much higher than a typical day with sales (about {typical}).",
                      **names, value=fmt_number(value), typical=fmt_number(median))
                    if value > median else
                    t("{metric_label} that day was {value}, much lower than a typical day with sales (about {typical}).",
                      **names, value=fmt_number(value), typical=fmt_number(median))
                )
                alerts.append(_alert(severity, t("Unusual day: {date}", date=_date_text(day)), text_key))

    # --- dependence on one product / region
    for field, noun in (("product", "product"), ("region", "region")):
        totals = group_totals(work, field)
        if len(totals) >= 2 and totals.sum() > 0 and (totals >= 0).all():
            share = float(totals.iloc[0] / totals.sum() * 100)
            if share >= 50:
                depend_title = (
                    t("Most {label} depends on one product", **names) if noun == "product"
                    else t("Most {label} depends on one region", **names)
                )
                alerts.append(_alert("medium", depend_title,
                    t("'{name}' brings {pct} of all {label}.", **names, name=totals.index[0],
                      pct=fmt_pct(share, signed=False))))

    # --- data problems
    negatives = int((work["revenue"] < 0).sum())
    if negatives and metric_label == "Revenue":
        alerts.append(_alert("info", t("Some sales are negative"),
            t("{count} row(s) have negative {label} (returns, refunds or typing mistakes).", **names, count=negatives)))
    if "date" in work:
        missing_dates = int(work["date"].isna().sum())
        if missing_dates:
            alerts.append(_alert("info", t("Some rows have no date"),
                t("{count} row(s) were left out of the time charts and comparisons.", count=missing_dates)))

    alerts.sort(key=lambda item: _SEVERITY_ORDER[item["severity"]])
    return alerts[:max_alerts]


# --------------------------------------------------------------------------
# 6. "What happened" in plain words
# --------------------------------------------------------------------------

def build_summary(work, kpis, periods=None, comparison=None, alerts=None, metric_label="Revenue"):
    """A few plain sentences, written by Python so they are always exact."""
    label = t(metric_label).lower()
    lines = []

    counting_records = metric_label == "Records"
    has_orders = "order_id" in work
    count = fmt_number(kpis["orders"])
    money = fmt_number(kpis["revenue"])
    if "date" in work and work["date"].notna().any():
        start, end = _date_text(work["date"].min()), _date_text(work["date"].max())
        if counting_records:
            lines.append(t("From {start} to {end} there are {count} records.", start=start, end=end, count=count))
        elif has_orders:
            lines.append(t("From {start} to {end} there were {count} orders and {money} in {label}.",
                           start=start, end=end, count=count, money=money, label=label))
        else:
            lines.append(t("From {start} to {end} there were {count} records and {money} in {label}.",
                           start=start, end=end, count=count, money=money, label=label))
    elif counting_records:
        lines.append(t("There are {count} records.", count=count))
    elif has_orders:
        lines.append(t("There are {count} orders with {money} in {label}.", count=count, money=money, label=label))
    else:
        lines.append(t("There are {count} records with {money} in {label}.", count=count, money=money, label=label))

    if comparison:
        change = comparison["change_pct"].get("revenue")
        n = periods["length_days"]
        if change is None:
            lines.append(t("In the last {n} days {label} was {current}; there is nothing in the {n} days before to compare with.",
                           n=n, label=label, current=fmt_number(comparison['current']['revenue'])))
        else:
            key = (
                "In the last {n} days {label} was {current}, up {pct} compared with the {n} days before ({previous})."
                if change >= 0 else
                "In the last {n} days {label} was {current}, down {pct} compared with the {n} days before ({previous})."
            )
            lines.append(t(key, n=n, label=label, current=fmt_number(comparison['current']['revenue']),
                           pct=fmt_pct(abs(change), signed=False), previous=fmt_number(comparison['previous']['revenue'])))

    for field, noun in (("product", "product"), ("region", "region")):
        totals = group_totals(work, field)
        if not totals.empty and totals.sum() > 0 and (totals >= 0).all():
            share = float(totals.iloc[0] / totals.sum() * 100)
            best_key = "Best product: {name} ({pct} of {label})." if noun == "product" else "Best region: {name} ({pct} of {label})."
            lines.append(t(best_key, name=totals.index[0], pct=fmt_pct(share, signed=False), label=label))

    urgent = [a for a in (alerts or []) if a["severity"] in ("high", "medium")]
    if urgent:
        lines.append(t("{count} thing(s) need your attention - see the alerts below.", count=len(urgent)))
    elif alerts is not None:
        lines.append(t("Nothing unusual was detected."))

    return lines


# --------------------------------------------------------------------------
# 7. Chart data
# --------------------------------------------------------------------------

def chart_over_time(work):
    """Revenue over time, grouped by day, week or month depending on how long the data is."""
    if "date" not in work:
        return None, ""
    valid = work.dropna(subset=["date"])
    if valid.empty:
        return None, ""
    span = int((valid["date"].max() - valid["date"].min()).days) + 1
    series = valid.set_index("date")["revenue"]
    if span <= 62:
        return series.resample("D").sum(), "day"
    if span <= 400:
        return series.resample("W").sum(), "week"
    return series.resample("MS").sum(), "month"


def chart_by_weekday(work):
    if "date" not in work:
        return None
    valid = work.dropna(subset=["date"])
    if valid.empty:
        return None
    totals = valid.groupby(valid["date"].dt.dayofweek)["revenue"].sum().reindex(range(7)).fillna(0.0)
    names = [t("Mon"), t("Tue"), t("Wed"), t("Thu"), t("Fri"), t("Sat"), t("Sun")]
    # The number keeps the bars in week order inside Streamlit charts.
    totals.index = [f"{i + 1}-{names[i]}" for i in range(7)]
    return totals


def top_n(work, field, n=10):
    totals = group_totals(work, field)
    return totals.head(n) if not totals.empty else None


# --------------------------------------------------------------------------
# 8. Facts for the AI
# --------------------------------------------------------------------------

def build_ai_analytics(work, periods=None, comparison=None, alerts=None, metric_label="Revenue"):
    """Facts for the AI: the generic analytics plus the comparison and the alerts."""
    roles = {}
    for column in work.columns:
        if column in ("revenue", "quantity", "unit_price"):
            roles[column] = "measure"
        elif column == "date":
            roles[column] = "date"
        elif column == "order_id":
            roles[column] = "id"
        else:
            roles[column] = "dimension"

    dimensions = [c for c in ("product", "category", "region") if c in work.columns]
    analytics = ga.build_generic_analytics(
        work,
        roles,
        main_measure="revenue",
        main_date="date" if "date" in work else None,
        dimensions=dimensions,
        aggregation="sum",
    )
    analytics["overview"]["settings"]["main_metric"] = f"revenue ({metric_label.lower()})"

    if comparison:
        analytics["comparison"] = {
            "latest_period": periods["current_label"],
            "previous_period": periods["previous_label"],
            "days_in_each_period": periods["length_days"],
            "revenue_latest": round(comparison["current"]["revenue"], 2),
            "revenue_previous": round(comparison["previous"]["revenue"], 2),
            "revenue_change_pct": None if comparison["change_pct"].get("revenue") is None
            else round(comparison["change_pct"]["revenue"], 1),
            "orders_latest": comparison["current"]["orders"],
            "orders_previous": comparison["previous"]["orders"],
        }

    if alerts:
        analytics["alerts"] = {
            f"alert_{i + 1}": f"{alert['title']}. {alert['detail']}" for i, alert in enumerate(alerts[:5])
        }

    return analytics


# --------------------------------------------------------------------------
# 9. Filters
# --------------------------------------------------------------------------

def apply_filters(work, date_range=None, regions=None, categories=None, products=None):
    """Filter the standard frame. Empty or None filters mean 'everything'."""
    out = work
    if date_range and "date" in out:
        start, end = date_range
        low, high = pd.Timestamp(start), pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        out = out[(out["date"] >= low) & (out["date"] <= high)]
    if regions and "region" in out:
        out = out[out["region"].isin(regions)]
    if categories and "category" in out:
        out = out[out["category"].isin(categories)]
    if products and "product" in out:
        out = out[out["product"].isin(products)]
    return out.reset_index(drop=True)
