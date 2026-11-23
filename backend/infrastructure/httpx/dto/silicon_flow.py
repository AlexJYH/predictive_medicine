from datetime import datetime

from backend.common.model.contract_model import ContractModel

class SiliconModelListResponse(ContractModel):
    id: str
    object: str | None = None
    created: int | None = None
    owned_by: str | None = None

class SiliconFileResponse(ContractModel):
    id: str
    object: str | None = None
    bytes: int | None = None
    created_at: int | None = None
    filename: str | None = None
    purpose: str | None = None
    line_count: int | None = None

class SiliconFlowTask(ContractModel):
    id: str | None = None
    object: str | None = None
    endpoint: str | None = None
    errors: str | None = None
    input_file_id: str | None = None
    completion_window: str | None = None
    status: str | None = None
    output_file_id: str | None = None
    error_file_id: str | None = None
    created_at: datetime | None = None
    in_progress_at: str | None = None
    expires_at: datetime | None = None
    finalizing_at: str | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    expired_at: datetime | None = None
    cancelling_at: datetime | None = None
    cancelled_at: datetime | None = None
    request_counts: str | None = None
    metadata: dict[str, str] | None = None
    file_name: str | None = None
    replace: dict[str, str] | None = None

class SiliconFlowTaskBatchResponse(ContractModel):
    object: str | None = None
    data: list[SiliconFlowTask]
    first_id: str | None = None
    last_id: str | None = None
    has_more: bool | None = None

class SiliconFlowVideoRequest(ContractModel):
    model: str | None = None
    prompt: str | None = None
    duration: int | None = None
    resolution: str | None = None
    ratio: str | None = None

class SiliconFlowVideoResponse(ContractModel):
    status: str | None = None
    reason: str | None = None
    result: dict[str,object] | None = None

class SiliconFlowVoiceListResponse(ContractModel):
    model: str | None = None
    custom_name: str | None = None
    text: str | None = None
    uri: str | None = None

class SiliconFlowImageResponse(ContractModel):
    images: dict[str, str] | None = None
    timings: dict[str, str] | None = None
    seed:int | None = None

class SiliconFlowMessage(ContractModel):
    role: str | None = None
    content: str | None = None
    reasoning_content: str | None = None

class SiliconFlowChoice(ContractModel):
    index: int | None = None
    message: SiliconFlowMessage | None = None
    finish_reason: str | None = None

class SiliconFlowCompletionToken(ContractModel):
    reasoning_tokens: int | None = None

class SiliconFlowPromptToken(ContractModel):
    cached_tokens: int | None = None

class SiliconFlowUsage(ContractModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    completion_tokens_details: SiliconFlowCompletionToken | None = None
    prompt_tokens_details: SiliconFlowPromptToken | None = None
    prompt_cache_hit_tokens: int | None = None
    prompt_cache_miss_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

class SiliconFlowContent(ContractModel):
    type: str | None = None
    thinking: str | None = None
    signature: str | None = None
    text: str | None = None

class SiliconFlowProperty(ContractModel):
    type: str | None = None
    noul: float | None = None

class SiliconFlowAnswer(ContractModel):
    property1: SiliconFlowProperty | None = None
    property2: SiliconFlowProperty | None = None

class SiliconFlowInsertionDate(ContractModel):
    object: str | None = None
    embedding: list[int] | None = None
    index: int | None = None

class SiliconFlowDocument(ContractModel):
    text: str | None = None

class SiliconFlowRerankResult(ContractModel):
    index: int | None = None
    document: SiliconFlowDocument | None = None
    relevance_score: float | None = None

class SiliconFlowToken(ContractModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    image_tokens: int | None = None

class SiliconFlowBilledUnit(ContractModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    image_tokens: int | None = None
    search_units: int | None = None
    classifications: int | None = None

class SiliconFlowMeta(ContractModel):
    tokens: SiliconFlowToken | None = None
    billed_units: SiliconFlowBilledUnit | None = None

class SiliconFlowChatResponse(ContractModel):
    id: str | None = None
    object: str | None = None
    created: int | None = None
    model: str | None = None
    choices: list[SiliconFlowChoice] | None = None
    usage: SiliconFlowUsage | None = None
    system_fingerprint: str | None = None
    role: str | None = None
    stop_reason: str | None = None
    stop_sequence: int | None = None
    type: str | None = None
    content: SiliconFlowContent | None = None
    answers: SiliconFlowAnswer | None = None
    data: list[SiliconFlowInsertionDate] | None = None
    results: list[SiliconFlowRerankResult] | None = None
    meta: SiliconFlowMeta | None = None

class SiliconFlowUrgent(ContractModel):
    type: str | None = None
    instructions: str | None = None

class SiliconFlowQuestion(ContractModel):
    is_urgent: SiliconFlowUrgent | None = None