import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from backend.config import settings
from backend.schemas import ChatRequest, ChatResponse, HealthResponse, MetricsResponse
from backend.vllm_client import vllm_client
from backend.logger import logger


app = FastAPI(
    title="LLM Serving Platform",
    description="基于 FastAPI + vLLM 的本地大模型推理服务平台",
    version="0.1.0",
)


metrics = {
    "total_requests": 0,
    "success_requests": 0,
    "failed_requests": 0,
    "total_latency_ms": 0.0,
}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    metrics["total_requests"] += 1

    temperature = request.temperature or settings.DEFAULT_TEMPERATURE
    max_tokens = request.max_tokens or settings.DEFAULT_MAX_TOKENS

    messages = [msg.model_dump() for msg in request.messages]

    try:
        result = vllm_client.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        metrics["success_requests"] += 1
        metrics["total_latency_ms"] += result["latency_ms"]
        
        logger.info(
            f"request_id={request_id} | "
            f"status=success | "
            f"prompt_chars={sum(len(m['content']) for m in messages)} | "
            f"prompt_tokens={result['prompt_tokens']} | "
            f"completion_tokens={result['completion_tokens']} | "
            f"total_tokens={result['total_tokens']} | "
            f"latency_ms={result['latency_ms']}"
        )

        return ChatResponse(
            request_id=request_id,
            model=result["model"],
            content=result["content"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            total_tokens=result["total_tokens"],
            latency_ms=result["latency_ms"],
        )

    except Exception as e:
        metrics["failed_requests"] += 1
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        metrics["total_latency_ms"] += latency_ms
        
        logger.error(
            f"request_id={request_id} | "
            f"status=failed | "
            f"latency_ms={latency_ms} | "
            f"error={str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "message": "LLM inference failed",
                "error": str(e),
            },
        )


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        vllm_base_url=settings.VLLM_BASE_URL,
        model=settings.MODEL_NAME,
    )


@app.get("/api/metrics", response_model=MetricsResponse)
def get_metrics():
    total = metrics["total_requests"]
    avg_latency = (
        metrics["total_latency_ms"] / total
        if total > 0
        else 0.0
    )

    return MetricsResponse(
        total_requests=metrics["total_requests"],
        success_requests=metrics["success_requests"],
        failed_requests=metrics["failed_requests"],
        avg_latency_ms=round(avg_latency, 2),
    )


@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    temperature = request.temperature or settings.DEFAULT_TEMPERATURE
    max_tokens = request.max_tokens or settings.DEFAULT_MAX_TOKENS
    messages = [msg.model_dump() for msg in request.messages]

def generate():
    try:
        for token in vllm_client.stream_chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield token

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            f"request_id={request_id} | "
            f"status=stream_success | "
            f"prompt_chars={sum(len(m['content']) for m in messages)} | "
            f"latency_ms={latency_ms}"
        )

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            f"request_id={request_id} | "
            f"status=stream_failed | "
            f"latency_ms={latency_ms} | "
            f"error={str(e)}"
        )
        yield f"\n[ERROR] request_id={request_id}, error={str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")