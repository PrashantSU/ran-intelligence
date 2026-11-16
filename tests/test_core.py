from ran_intelligence.core.config import Settings, get_settings
from ran_intelligence.core.exceptions import (
    DataError,
    DataNotFoundError,
    DataValidationError,
    RANIntelligenceError,
)
from ran_intelligence.core.logging_config import configure_logging, get_logger


def test_default_settings():
    settings = Settings()
    assert settings.app_name == "RAN Intelligence Platform"
    assert settings.app_env == "development"
    assert settings.log_level == "INFO"


def test_settings_cache():
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second


def test_exception_inheritance():
    assert issubclass(DataError, RANIntelligenceError)
    assert issubclass(DataNotFoundError, DataError)
    assert issubclass(DataValidationError, DataError)


def test_custom_exception_details():
    error = DataValidationError(
        "Invalid measurement",
        details={"cell_id": "CELL_001"},
    )
    assert error.message == "Invalid measurement"
    assert error.details["cell_id"] == "CELL_001"


def test_logging_configuration():
    configure_logging()
    logger = get_logger()
    assert logger is not None
