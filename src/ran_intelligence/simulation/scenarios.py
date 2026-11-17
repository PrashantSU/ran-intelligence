
"""Reusable scenarios and what-if transformations for the RAN digital twin."""

from dataclasses import replace

from ran_intelligence.simulation.digital_twin import (
    Cell,
    NetworkScenario,
    UserEquipment,
)


def create_reference_scenario() -> NetworkScenario:
    """Create a deterministic multi-cell reference network."""
    cells = (
        Cell(
            cell_id="cell_001",
            x_m=0,
            y_m=0,
            tx_power_dbm=46,
            bandwidth_mhz=20,
        ),
        Cell(
            cell_id="cell_002",
            x_m=500,
            y_m=0,
            tx_power_dbm=46,
            bandwidth_mhz=20,
        ),
        Cell(
            cell_id="cell_003",
            x_m=250,
            y_m=430,
            tx_power_dbm=43,
            bandwidth_mhz=20,
        ),
    )

    users = (
        UserEquipment("ue_001", 80, 60, 12),
        UserEquipment("ue_002", 160, 30, 20),
        UserEquipment("ue_003", 350, 60, 15),
        UserEquipment("ue_004", 430, 100, 25),
        UserEquipment("ue_005", 230, 280, 18),
        UserEquipment("ue_006", 300, 350, 22),
        UserEquipment("ue_007", 250, 180, 30),
        UserEquipment("ue_008", 100, 200, 10),
        UserEquipment("ue_009", 400, 250, 16),
        UserEquipment("ue_010", 250, 80, 12),
    )

    return NetworkScenario(
        cells=cells,
        users=users,
        scenario_name="baseline",
    )


def change_transmit_power(
    scenario: NetworkScenario,
    cell_id: str,
    tx_power_dbm: float,
) -> NetworkScenario:
    """Change the transmit power of one cell."""
    if not -10 <= tx_power_dbm <= 60:
        raise ValueError("tx_power_dbm must be between -10 and 60")

    if not any(cell.cell_id == cell_id for cell in scenario.cells):
        raise ValueError(f"Unknown cell: {cell_id}")

    cells = tuple(
        replace(cell, tx_power_dbm=tx_power_dbm)
        if cell.cell_id == cell_id else cell
        for cell in scenario.cells
    )

    return replace(
        scenario,
        cells=cells,
        scenario_name=f"{scenario.scenario_name}_power_{cell_id}",
    )


def simulate_cell_outage(
    scenario: NetworkScenario,
    cell_id: str,
) -> NetworkScenario:
    """Deactivate a cell to study outage impact."""
    if not any(cell.cell_id == cell_id for cell in scenario.cells):
        raise ValueError(f"Unknown cell: {cell_id}")

    if sum(cell.active for cell in scenario.cells) <= 1:
        raise ValueError("Cannot deactivate the only active cell")

    cells = tuple(
        replace(cell, active=False) if cell.cell_id == cell_id else cell
        for cell in scenario.cells
    )

    return replace(
        scenario,
        cells=cells,
        scenario_name=f"{scenario.scenario_name}_outage_{cell_id}",
    )


def change_interference(
    scenario: NetworkScenario,
    cell_id: str,
    interference_scale: float,
) -> NetworkScenario:
    """Adjust the interference contribution of a cell."""
    if interference_scale < 0:
        raise ValueError("interference_scale must be non-negative")

    if not any(cell.cell_id == cell_id for cell in scenario.cells):
        raise ValueError(f"Unknown cell: {cell_id}")

    cells = tuple(
        replace(cell, interference_scale=interference_scale)
        if cell.cell_id == cell_id else cell
        for cell in scenario.cells
    )

    return replace(
        scenario,
        cells=cells,
        scenario_name=f"{scenario.scenario_name}_interference_{cell_id}",
    )


def move_user(
    scenario: NetworkScenario,
    ue_id: str,
    x_m: float,
    y_m: float,
) -> NetworkScenario:
    """Move one UE to a new coordinate."""
    if not any(user.ue_id == ue_id for user in scenario.users):
        raise ValueError(f"Unknown UE: {ue_id}")

    users = tuple(
        replace(user, x_m=x_m, y_m=y_m) if user.ue_id == ue_id else user
        for user in scenario.users
    )

    return replace(
        scenario,
        users=users,
        scenario_name=f"{scenario.scenario_name}_move_{ue_id}",
    )
