from dataclasses import dataclass
from enum import StrEnum


class Classification(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"


class ModelTrustBoundary(StrEnum):
    INTERNAL = "internal"
    EXTERNAL_APPROVED = "external_approved"
    EXTERNAL_UNAPPROVED = "external_unapproved"


class ModelOperation(StrEnum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANK = "rerank"


@dataclass(frozen=True)
class ModelRequest:
    classification: Classification
    trust_boundary: ModelTrustBoundary
    operation: ModelOperation
    internal_model_approved_for_restricted: bool = False
    has_active_external_exception: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def evaluate_model_request(request: ModelRequest) -> PolicyDecision:
    """Apply the default-deny policy before any provider SDK can be invoked."""
    if request.trust_boundary is ModelTrustBoundary.EXTERNAL_UNAPPROVED:
        return PolicyDecision(False, "unapproved_external_model")
    if request.classification is Classification.PUBLIC:
        return PolicyDecision(True, "public_content")
    if request.classification is Classification.RESTRICTED:
        if request.trust_boundary is ModelTrustBoundary.INTERNAL and request.internal_model_approved_for_restricted:
            return PolicyDecision(True, "approved_internal_model")
        return PolicyDecision(False, "restricted_content_requires_approved_internal_model")
    if request.trust_boundary is ModelTrustBoundary.INTERNAL:
        return PolicyDecision(True, "internal_model")
    if request.has_active_external_exception:
        return PolicyDecision(True, "active_external_exception")
    return PolicyDecision(False, "internal_content_requires_active_external_exception")
