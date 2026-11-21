from backend.infrastructure.runtime import get_resources
from backend.repository.llm_model.postgres import PostgresLLMModelRepository
from backend.services.llm.silicon_flow.services.silicon_non_stream import SiliconNonStreamService
from backend.services.llm.vendor_model.services.llm_model import LLMModelService


def get_llm_model_service() -> LLMModelService:
    resources = get_resources()
    return LLMModelService(
        repository=PostgresLLMModelRepository(),
        session_factory=resources.session_factory,
        id_generator=resources.id_generator,
        llm_vendor_setting=resources.llm_vendor_setting,
    )

def get_silicon_service() -> SiliconNonStreamService:
    resources = get_resources()
    return SiliconNonStreamService(
        session_factory=resources.session_factory,
        id_generator=resources.id_generator,
        llm_model_service=get_llm_model_service(),
    )