"""Standard data schemas for RAN measurements."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeasurementRecord(BaseModel):
    """Standardised representation of one RAN measurement."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    measurement_id: int
    timestamp: datetime

    longitude: float
    latitude: float
    altitude_m: float

    lte_cell_id: int | None = None
    lte_rsrp_dbm: float | None = None
    lte_sinr_db: float | None = None

    nr_cell_id: int | None = None
    nr_rsrp_dbm: float | None = None
    nr_sinr_db: float | None = None
    nr_cqi: float | None = None
    nr_mcs: float | None = None
    nr_rank_indicator: float | None = None

    # Original throughput unit has not yet been established.
    throughput_raw: float | None = None


REQUIRED_COLUMNS = [
    "session_id",
    "measurement_id",
    "timestamp",
    "longitude",
    "latitude",
    "altitude_m",
]

OPTIONAL_COLUMNS = [
    "lte_cell_id",
    "lte_rsrp_dbm",
    "lte_sinr_db",
    "nr_cell_id",
    "nr_rsrp_dbm",
    "nr_sinr_db",
    "nr_cqi",
    "nr_mcs",
    "nr_rank_indicator",
    "throughput_raw",
]

ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
