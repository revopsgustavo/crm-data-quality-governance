from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

import pandas as pd


def _safe_float(value: object) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def format_currency_br(value: object) -> str:
    number = _safe_float(value)
    formatted = f"{number:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def format_number_br(value: object) -> str:
    number = _safe_float(value)
    return f"{number:,.1f}".replace(",", "_").replace(".", ",").replace("_", ".")


def format_integer_br(value: object) -> str:
    number = int(round(_safe_float(value)))
    return f"{number:,}".replace(",", ".")


def format_percent_br(value: object) -> str:
    number = _safe_float(value) * 100
    return f"{number:,.1f}%".replace(",", "_").replace(".", ",").replace("_", ".")


def format_points_br(value: object) -> str:
    number = _safe_float(value) * 100
    return f"{number:,.1f} pts".replace(",", "_").replace(".", ",").replace("_", ".")


def format_date_br(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return ""
    return parsed.strftime("%d/%m/%Y")


def select_existing(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    return df[[column for column in columns if column in df.columns]].copy()


def has_columns(df: pd.DataFrame, columns: Iterable[str]) -> bool:
    return all(column in df.columns for column in columns)


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator in (0, 0.0) or pd.isna(denominator):
        return 0.0
    return float(numerator) / float(denominator)
