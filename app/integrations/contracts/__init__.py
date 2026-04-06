"""Shared integration contract types for external providers."""

from .result_envelope import ExternalResultEnvelope, ExternalResultError
from .types import (
    IntegrationAuthModel,
    IntegrationExecutionMode,
    IntegrationProviderKey,
    IntegrationResultStatus,
    IntegrationTargetKind,
    ExternalArtifactReference,
    SuperglueConnectorBinding,
    SuperglueSystemBinding,
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
    "ExternalArtifactReference",
    "SuperglueConnectorBinding",
    "SuperglueSystemBinding",
    "SuperglueToolRecord",
]
