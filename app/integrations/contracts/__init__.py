"""Shared integration contract types for external providers."""

from .result_envelope import ExternalResultEnvelope, ExternalResultError
from .types import (
    IntegrationAuthModel,
    IntegrationExecutionMode,
    IntegrationProviderKey,
    IntegrationResultStatus,
    IntegrationTargetKind,
    SuperglueToolRecord,
)

__all__ = [
    "ExternalResultEnvelope",
    "ExternalResultError",
    "IntegrationAuthModel",
    "IntegrationExecutionMode",
    "IntegrationProviderKey",
    "IntegrationResultStatus",
    "IntegrationTargetKind",
    "SuperglueToolRecord",
]
