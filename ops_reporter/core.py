from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "date",
    "department",
    "operator",
    "units_produced",
    "defects",
    "downtime_minutes",
    "target_units",
}


@dataclass(frozen=True)
class ReportMetrics:
    total_units: int
    total_defects: int
    total_downtime_minutes: int
    target_units: int
    quality_rate: float
    target_attainment: float


def load_data(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Input file does not exist: {source}")
    if source.suffix.lower() == ".csv":
        frame = pd.read_csv(source)
    elif source.suffix.lower() in {".xlsx", ".xlsm"}:
        frame = pd.read_excel(source)
    else:
        raise ValueError("Input must be a CSV or XLSX file")
    return validate_data(frame)


def validate_data(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    if normalized.columns.duplicated().any():
        raise ValueError("Duplicate columns after normalization")
    missing = REQUIRED_COLUMNS - set(normalized.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    normalized = normalized[sorted(REQUIRED_COLUMNS)]
    if normalized.empty:
        raise ValueError("Input must contain at least one row")
    for column in ("department", "operator"):
        if normalized[column].isna().any():
            raise ValueError(f"Column '{column}' cannot contain missing labels")
        normalized[column] = normalized[column].astype(str).str.strip()
        if normalized[column].eq("").any():
            raise ValueError(f"Column '{column}' cannot contain blank labels")
    normalized["date"] = pd.to_datetime(normalized["date"], errors="raise")
    if normalized["date"].isna().any():
        raise ValueError("Column 'date' cannot contain missing dates")
    for column in ["units_produced", "defects", "downtime_minutes", "target_units"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="raise")
        if not normalized[column].map(math.isfinite).all():
            raise ValueError(f"Column '{column}' must contain finite numbers")
        if (normalized[column] % 1 != 0).any():
            raise ValueError(f"Column '{column}' must contain whole numbers")
        if (normalized[column] < 0).any():
            raise ValueError(f"Column '{column}' cannot contain negative values")
    if (normalized["defects"] > normalized["units_produced"]).any():
        raise ValueError("Defects cannot be greater than units produced")
    return normalized.sort_values(["date", "department", "operator"]).reset_index(drop=True)


def calculate_metrics(frame: pd.DataFrame) -> ReportMetrics:
    units = int(frame["units_produced"].sum())
    defects = int(frame["defects"].sum())
    target = int(frame["target_units"].sum())
    downtime = int(frame["downtime_minutes"].sum())
    return ReportMetrics(
        total_units=units,
        total_defects=defects,
        total_downtime_minutes=downtime,
        target_units=target,
        quality_rate=(units - defects) / units if units else 0.0,
        target_attainment=units / target if target else 0.0,
    )


def department_summary(frame: pd.DataFrame) -> pd.DataFrame:
    result = (
        frame.groupby("department", as_index=False)
        .agg(
            units_produced=("units_produced", "sum"),
            defects=("defects", "sum"),
            downtime_minutes=("downtime_minutes", "sum"),
            target_units=("target_units", "sum"),
        )
        .sort_values("units_produced", ascending=False)
    )
    result["quality_rate"] = (result["units_produced"] - result["defects"]) / result["units_produced"].replace(0, pd.NA)
    result["target_attainment"] = result["units_produced"] / result["target_units"].replace(0, pd.NA)
    return result.fillna(0)


def daily_summary(frame: pd.DataFrame) -> pd.DataFrame:
    result = (
        frame.groupby("date", as_index=False)
        .agg(
            units_produced=("units_produced", "sum"),
            defects=("defects", "sum"),
            downtime_minutes=("downtime_minutes", "sum"),
            target_units=("target_units", "sum"),
        )
        .sort_values("date")
    )
    result["quality_rate"] = (result["units_produced"] - result["defects"]) / result["units_produced"].replace(0, pd.NA)
    result["target_attainment"] = result["units_produced"] / result["target_units"].replace(0, pd.NA)
    return result.fillna(0)
