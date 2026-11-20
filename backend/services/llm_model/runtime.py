from backend.infrastructure.runtime import get_async_session_factory, get_id_generator, get_resources
from backend.repository.llm_model.postgres import PostgresLLMModelRepository
from backend.services.llm_model.services.llm_model import LLMModelService


def get_llm_model_service() -> LLMModelService:
    resources = get_resources()
    return LLMModelService(
        repository=PostgresLLMModelRepository(),
        session_factory=resources.session_factory,
        id_generator=resources.id_generator,
        llm_vendor_setting=resources.llm_vendor_setting,
    )