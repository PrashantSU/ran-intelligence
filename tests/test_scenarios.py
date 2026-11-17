
from dataclasses import replace

import pytest

from ran_intelligence.simulation.digital_twin import simulate_network
from ran_intelligence.simulation.scenarios import (
    change_interference,
    change_transmit_power,
    create_reference_scenario,
    move_user,
    simulate_cell_outage,
)


def test_reference_scenario():
    scenario = create_reference_scenario()
    assert len(scenario.cells) == 3
    assert len(scenario.users) == 10


def test_transmit_power_change():
    scenario = create_reference_scenario()
    updated = change_transmit_power(scenario, "cell_001", 50)
    cell = next(c for c in updated.cells if c.cell_id == "cell_001")
    assert cell.tx_power_dbm == 50
    assert scenario.cells[0].tx_power_dbm == 46


def test_cell_outage():
    scenario = create_reference_scenario()
    updated = simulate_cell_outage(scenario, "cell_001")
    assert sum(c.active for c in updated.cells) == 2
    assert simulate_network(updated)["summary"]["active_cells"] == 2


def test_interference_change():
    scenario = create_reference_scenario()
    updated = change_interference(scenario, "cell_002", 2.0)
    cell = next(c for c in updated.cells if c.cell_id == "cell_002")
    assert cell.interference_scale == 2.0


def test_move_user():
    scenario = create_reference_scenario()
    updated = move_user(scenario, "ue_001", 300, 300)
    user = next(u for u in updated.users if u.ue_id == "ue_001")
    assert (user.x_m, user.y_m) == (300, 300)


def test_unknown_cell_rejected():
    with pytest.raises(ValueError, match="Unknown cell"):
        change_transmit_power(create_reference_scenario(), "missing", 40)


def test_last_active_cell_cannot_be_disabled():
    scenario = create_reference_scenario()
    single_cell = replace(scenario, cells=(scenario.cells[0],))
    with pytest.raises(ValueError, match="only active cell"):
        simulate_cell_outage(single_cell, "cell_001")


def test_unknown_ue_rejected():
    with pytest.raises(ValueError, match="Unknown UE"):
        move_user(create_reference_scenario(), "missing", 0, 0)


def test_scenarios_do_not_mutate_original():
    scenario = create_reference_scenario()
    change_transmit_power(scenario, "cell_001", 50)
    assert scenario.cells[0].tx_power_dbm == 46
