import time
from typing import List, Dict, Any, Generator

from openai import OpenAI

from backend.config import settings


class VLLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.VLLM_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)

        content = response.choices[0].message.content

        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return {
            "model": settings.MODEL_NAME,
            "content": content,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms,
        }

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> Generator[str, None, None]:
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content


vllm_client = VLLMClient()