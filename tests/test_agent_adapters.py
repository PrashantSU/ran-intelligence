from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from ran_intelligence.agents.adapters import (
    create_investigation_toolbox,
    filter_incident_measurements,
)
from ran_intelligence.agents.schemas import IncidentRequest


@pytest.fixture
def incident():
    start = datetime(2026, 11, 18, 10, tzinfo=UTC)
    return IncidentRequest(
        description="SINR degradation",
        session_id="session_a",
        cell_id="1",
        start_time=start,
        end_time=start + timedelta(minutes=5),
        severity="high",
        suspected_kpis=["lte_sinr_db"],
    )


@pytest.fixture
def measurements():
    timestamps = pd.date_range(
        "2026-11-18T10:00:00Z",
        periods=20,
        freq="15s",
    )

    return pd.DataFrame({
        "session_id": ["session_a"] * 20,
        "timestamp": timestamps,
        "lte_cell_id": [1] * 20,
        "nr_cell_id": [1] * 20,
        "lte_rsrp_dbm": [-80.0] * 20,
        "lte_sinr_db": [15.0] * 19 + [2.0],
        "nr_rsrp_dbm": [-101.0] * 20,
        "nr_sinr_db": [25.0] * 20,
        "nr_cqi": [10.0] * 20,
        "nr_mcs": [17.0] * 20,
        "nr_rank_indicator": [2.0] * 20,
        "throughput_raw": [20.0] * 20,
    })


def test_filter_incident_measurements(incident, measurements):
    result = filter_incident_measurements(measurements, incident)

    assert len(result) == 20
    assert set(result["session_id"]) == {"session_a"}


def test_filter_rejects_empty_incident_window(incident, measurements):
    incident.session_id = "missing_session"

    with pytest.raises(ValueError, match="No measurements match"):
        filter_incident_measurements(measurements, incident)


def test_filter_applies_cell_identifier(incident, measurements):
    measurements.loc[:, "lte_cell_id"] = 2
    measurements.loc[:, "nr_cell_id"] = 2

    with pytest.raises(ValueError, match="No measurements match"):
        filter_incident_measurements(measurements, incident)


def test_kpi_adapter_uses_real_kpi_module(incident, measurements):
    toolbox = create_investigation_toolbox(
        measurements,
        include_simulation=False,
    )

    result = toolbox.run("kpi", incident)

    print("ANOMALY ADAPTER ERROR:", result.error)
    assert result.status == "success", f"Adapter error: {result.error!r}"
    assert len(result.evidence) == 1
    assert result.evidence[0].evidence_type == "kpi"


def test_anomaly_adapter_counts_only_flagged_observations(
    incident,
    measurements,
):
    toolbox = create_investigation_toolbox(
        measurements,
        include_simulation=False,
    )

    result = toolbox.run("anomaly", incident)

    assert result.status == "success", f"Adapter error: {result.error!r}"
    assert result.evidence[0].evidence_type == "anomaly"

    metadata = result.evidence[0].metadata

    assert metadata["evaluated_observation_count"] >= 20
    assert metadata["anomaly_count"] < metadata["evaluated_observation_count"]

    samples = metadata["anomaly_samples"]["records"]
    assert samples
    assert all(sample["is_anomaly"] for sample in samples)


def test_anomaly_adapter_reports_zero_when_no_anomalies(
    incident,
    measurements,
):
    measurements["lte_sinr_db"] = 15.0

    toolbox = create_investigation_toolbox(
        measurements,
        include_simulation=False,
    )

    result = toolbox.run("anomaly", incident)

    assert result.status == "success", f"Adapter error: {result.error!r}"

    metadata = result.evidence[0].metadata

    assert metadata["anomaly_count"] == 0
    assert metadata["anomaly_samples"]["row_count"] == 0


def test_rag_handler_is_optional(incident, measurements):
    toolbox = create_investigation_toolbox(
        measurements,
        include_simulation=False,
    )

    result = toolbox.run("rag", incident)

    assert result.status == "unavailable"


def test_rag_handler_can_be_injected(incident, measurements):
    toolbox = create_investigation_toolbox(
        measurements,
        rag_handler=lambda request: {
            "retrieved_documents": 3,
            "answer": "Relevant technical evidence retrieved.",
        },
        include_simulation=False,
    )

    result = toolbox.run("rag", incident)

    assert result.status == "success", f"Adapter error: {result.error!r}"
    assert result.evidence[0].evidence_type == "rag"


def test_anomaly_adapter_uses_only_supported_suspected_kpis(
    incident,
    measurements,
):
    incident.suspected_kpis = ["lte_sinr_db"]

    toolbox = create_investigation_toolbox(
        measurements,
        include_simulation=False,
    )

    result = toolbox.run("anomaly", incident)

    assert result.status == "success", f"Adapter error: {result.error!r}"

    metadata = result.evidence[0].metadata

    assert metadata["metrics"] == ["lte_sinr_db"]
    assert all(
        sample["kpi"] == "lte_sinr_db"
        for sample in metadata["anomaly_samples"]["records"]
    )
