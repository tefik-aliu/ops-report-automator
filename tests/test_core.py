import pandas as pd
import pytest

from ops_reporter.core import calculate_metrics, department_summary, validate_data


def sample_frame():
    return pd.DataFrame([
        {"date":"2026-07-01","department":"Cutting","operator":"A","units_produced":100,"defects":2,"downtime_minutes":10,"target_units":110},
        {"date":"2026-07-01","department":"Assembly","operator":"B","units_produced":80,"defects":1,"downtime_minutes":5,"target_units":80},
    ])


def test_metrics_are_calculated():
    metrics = calculate_metrics(validate_data(sample_frame()))
    assert metrics.total_units == 180
    assert metrics.total_defects == 3
    assert metrics.quality_rate == pytest.approx(177/180)
    assert metrics.target_attainment == pytest.approx(180/190)


def test_department_summary():
    result = department_summary(validate_data(sample_frame()))
    assert set(result["department"]) == {"Cutting", "Assembly"}
    assert "target_attainment" in result.columns


def test_missing_columns_fail_fast():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_data(pd.DataFrame({"date":["2026-01-01"]}))


def test_negative_values_are_rejected():
    frame = sample_frame()
    frame.loc[0, "defects"] = -1
    with pytest.raises(ValueError, match="cannot contain negative"):
        validate_data(frame)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf"), 1.5])
@pytest.mark.parametrize("column", ["units_produced", "defects", "downtime_minutes", "target_units"])
def test_invalid_numeric_values_cannot_silently_change_totals(column, value):
    frame = sample_frame().astype({column: float})
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match="finite|whole"):
        validate_data(frame)


@pytest.mark.parametrize("column,value", [("date", None), ("department", "  "), ("operator", None)])
def test_missing_group_keys_are_rejected(column, value):
    frame = sample_frame()
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match="missing|blank"):
        validate_data(frame)


def test_empty_data_is_rejected():
    with pytest.raises(ValueError, match="at least one"):
        validate_data(sample_frame().iloc[:0])


def test_duplicate_normalized_headers_are_rejected():
    frame = sample_frame()
    frame[" Department "] = "Other"
    with pytest.raises(ValueError, match="Duplicate"):
        validate_data(frame)
