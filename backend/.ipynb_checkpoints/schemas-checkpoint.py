from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="消息角色，例如 system/user/assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4096)


class ChatResponse(BaseModel):
    request_id: str
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    vllm_base_url: str
    model: str


class MetricsResponse(BaseModel):
    total_requests: int
    success_requests: int
    failed_requests: int
    avg_latency_ms: float