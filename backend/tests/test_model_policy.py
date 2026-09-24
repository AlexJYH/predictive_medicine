import pytest
from fastapi.testclient import TestClient

from app.main import app

from app.domain.model_policy import (
    Classification,
    ModelRequest,
    ModelTrustBoundary,
    evaluate_model_request,
)


@pytest.mark.parametrize(
    ("model_request", "expected"),
    [
        (ModelRequest(Classification.PUBLIC, ModelTrustBoundary.EXTERNAL_APPROVED, "chat"), True),
        (ModelRequest(Classification.INTERNAL, ModelTrustBoundary.EXTERNAL_APPROVED, "embedding"), False),
        (ModelRequest(Classification.RESTRICTED, ModelTrustBoundary.EXTERNAL_APPROVED, "rerank"), False),
        (ModelRequest(Classification.RESTRICTED, ModelTrustBoundary.INTERNAL, "chat", True), True),
        (ModelRequest(Classification.PUBLIC, ModelTrustBoundary.EXTERNAL_UNAPPROVED, "chat"), False),
    ],
)
def test_default_model_egress_policy(model_request: ModelRequest, expected: bool) -> None:
    assert evaluate_model_request(model_request).allowed is expected


def test_bootstrap_exposes_no_sensitive_configuration() -> None:
    response = TestClient(app).get("/api/v1/app/bootstrap")
    assert response.status_code == 200
    assert response.json()["capabilities"] == ["knowledge_bases", "document_ingestion", "cited_answers"]
