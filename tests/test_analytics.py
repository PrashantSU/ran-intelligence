import pandas as pd
import pytest

from ran_intelligence.analytics.kpi import (
    build_kpi_timeseries,
    compute_kpi_summary,
    compute_session_summary,
    get_available_kpis,
)


@pytest.fixture
def sample_measurements():
    return pd.DataFrame(
        {
            "session_id": ["A", "A", "A", "B"],
            "measurement_id": [1, 2, 3, 1],
            "timestamp": pd.to_datetime(
                [
                    "2023-01-01 10:00:00",
                    "2023-01-01 10:00:20",
                    "2023-01-01 10:01:00",
                    "2023-01-02 10:00:00",
                ]
            ),
            "lte_rsrp_dbm": [-80.0, -82.0, None, -75.0],
            "lte_sinr_db": [15.0, 17.0, 16.0, 20.0],
            "nr_rsrp_dbm": [-100.0, -102.0, None, -95.0],
            "nr_sinr_db": [20.0, 22.0, None, 25.0],
            "nr_cqi": [10.0, 11.0, 12.0, 13.0],
            "nr_mcs": [15.0, 16.0, 17.0, 18.0],
            "nr_rank_indicator": [1.0, 2.0, 2.0, 1.0],
            "throughput_raw": [100.0, None, 120.0, 200.0],
        }
    )


def test_kpi_definitions_include_unverified_throughput_unit():
    definitions = get_available_kpis()
    throughput = next(item for item in definitions if item["column"] == "throughput_raw")
    assert throughput["unit"] == "source units (unverified)"


def test_kpi_summary_calculates_statistics_and_missingness(sample_measurements):
    result = compute_kpi_summary(sample_measurements)
    row = result[(result["session_id"] == "A") & (result["kpi"] == "lte_rsrp_dbm")].iloc[0]

    assert row["valid_observations"] == 2
    assert row["missing_observations"] == 1
    assert row["median"] == -81.0


def test_session_summary_calculates_throughput_coverage(sample_measurements):
    result = compute_session_summary(sample_measurements)
    row = result[result["session_id"] == "A"].iloc[0]

    assert row["total_observations"] == 3
    assert row["unique_measurements"] == 3
    assert row["throughput_observations"] == 2
    assert row["throughput_coverage_pct"] == pytest.approx(200 / 3)


def test_timeseries_aggregates_values_and_counts(sample_measurements):
    result = build_kpi_timeseries(
        sample_measurements,
        session_id="A",
        metric="lte_sinr_db",
        interval="1min",
        aggregation="median",
    )

    assert len(result) == 2
    assert result.loc[0, "value"] == 16.0
    assert result.loc[0, "sample_count"] == 2
    assert result.loc[1, "sample_count"] == 1


def test_timeseries_rejects_unknown_metric(sample_measurements):
    with pytest.raises(ValueError, match="Unsupported KPI"):
        build_kpi_timeseries(sample_measurements, "A", "unknown_metric")
