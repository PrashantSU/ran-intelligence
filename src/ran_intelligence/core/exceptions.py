"""Application-wide exception definitions."""


class RANIntelligenceError(Exception):
    """Base exception for the RAN Intelligence Platform."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(RANIntelligenceError):
    """Raised when application configuration is invalid."""


class DataError(RANIntelligenceError):
    """Base exception for data-related failures."""


class DataNotFoundError(DataError):
    """Raised when a requested dataset or file cannot be found."""


class DataValidationError(DataError):
    """Raised when network measurement data fails validation."""


class ProcessingError(RANIntelligenceError):
    """Raised when a processing operation fails."""


class ModelError(RANIntelligenceError):
    """Raised when an ML model operation fails."""


class RetrievalError(RANIntelligenceError):
    """Raised when document retrieval fails."""


class InvestigationError(RANIntelligenceError):
    """Raised when an incident investigation cannot be completed."""
