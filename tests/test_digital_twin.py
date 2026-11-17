
from dataclasses import replace

import pytest

from ran_intelligence.simulation.digital_twin import (
    Cell,
    NetworkScenario,
    UserEquipment,
    compare_scenarios,
    dbm_to_mw,
    mw_to_dbm,
    path_loss_db,
    shannon_spectral_efficiency,
    simulate_network,
)


@pytest.fixture
def scenario():
    cells = (
        Cell("cell_1", 0, 0, tx_power_dbm=46, bandwidth_mhz=20),
        Cell("cell_2", 500, 0, tx_power_dbm=46, bandwidth_mhz=20),
    )
    users = (
        UserEquipment("ue_1", 100, 0, demand_mbps=20),
        UserEquipment("ue_2", 200, 50, demand_mbps=30),
        UserEquipment("ue_3", 400, 0, demand_mbps=15),
    )
    return NetworkScenario(cells=cells, users=users)


def test_dbm_mw_conversion():
    assert dbm_to_mw(0) == pytest.approx(1.0)
    assert mw_to_dbm(1.0) == pytest.approx(0.0)


def test_path_loss_increases_with_distance():
    near = path_loss_db(100)
    far = path_loss_db(200)
    assert far > near


def test_spectral_efficiency_increases_with_sinr():
    assert shannon_spectral_efficiency(10) > shannon_spectral_efficiency(0)


def test_simulation_returns_all_users_and_cells(scenario):
    result = simulate_network(scenario)
    assert len(result["ue_metrics"]) == 3
    assert len(result["cell_metrics"]) == 2
    assert result["summary"]["ue_count"] == 3


def test_ue_association_uses_strongest_cell(scenario):
    result = simulate_network(scenario)
    associations = result["ue_metrics"].set_index("ue_id")["serving_cell"]
    assert associations["ue_1"] == "cell_1"
    assert associations["ue_3"] == "cell_2"


def test_radio_metrics_are_finite(scenario):
    result = simulate_network(scenario)
    assert result["ue_metrics"]["sinr_db"].map(
        lambda value: value == value
    ).all()
    assert (result["ue_metrics"]["throughput_mbps"] >= 0).all()


def test_throughput_does_not_exceed_demand(scenario):
    result = simulate_network(scenario)
    metrics = result["ue_metrics"]
    assert (metrics["throughput_mbps"] <= metrics["demand_mbps"] + 1e-9).all()


def test_cell_outage_changes_association(scenario):
    outage = replace(
        scenario,
        cells=(scenario.cells[0], replace(scenario.cells[1], active=False)),
    )
    result = simulate_network(outage)
    assert set(result["ue_metrics"]["serving_cell"]) == {"cell_1"}


def test_scenario_comparison(scenario):
    alternative = replace(
        scenario,
        scenario_name="higher_power",
        cells=(
            replace(scenario.cells[0], tx_power_dbm=50),
            scenario.cells[1],
        ),
    )
    comparison = compare_scenarios(scenario, alternative)
    assert "change" in comparison.columns
    assert len(comparison) == 5


def test_duplicate_cell_ids_rejected():
    cell = Cell("same", 0, 0)
    with pytest.raises(ValueError, match="unique"):
        NetworkScenario(
            cells=(cell, cell),
            users=(UserEquipment("ue", 10, 10),),
        )


def test_invalid_bandwidth_rejected():
    with pytest.raises(ValueError, match="bandwidth"):
        Cell("bad", 0, 0, bandwidth_mhz=0)


def test_no_active_cells_rejected():
    scenario = NetworkScenario(
        cells=(Cell("cell_1", 0, 0, active=False),),
        users=(UserEquipment("ue_1", 10, 10),),
    )
    with pytest.raises(ValueError, match="active"):
        simulate_network(scenario)
