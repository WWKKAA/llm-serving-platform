import asyncio
import time
import statistics
from typing import List, Dict, Any

import httpx


API_URL = "http://127.0.0.1:8080/api/chat"


DEFAULT_PAYLOAD = {
    "messages": [
        {
            "role": "user",
            "content": "请用三句话解释什么是 vLLM。"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 128
}


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    index = int(len(values) * p / 100)

    if index >= len(values):
        index = len(values) - 1

    return values[index]


async def send_one_request(
    client: httpx.AsyncClient,
    request_id: int,
) -> Dict[str, Any]:
    start_time = time.perf_counter()

    try:
        response = await client.post(
            API_URL,
            json=DEFAULT_PAYLOAD,
            timeout=120,
        )

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        if response.status_code == 200:
            data = response.json()

            return {
                "request_id": request_id,
                "success": True,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "prompt_tokens": data.get("prompt_tokens", 0),
                "completion_tokens": data.get("completion_tokens", 0),
                "total_tokens": data.get("total_tokens", 0),
                "error": None,
            }

        return {
            "request_id": request_id,
            "success": False,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "error": response.text,
        }

    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        return {
            "request_id": request_id,
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "error": repr(e),
        }


async def run_benchmark(total_requests: int, concurrency: int):
    print("=" * 60)
    print("普通问答接口压测开始")
    print(f"API URL: {API_URL}")
    print(f"总请求数: {total_requests}")
    print(f"并发数: {concurrency}")
    print("=" * 60)

    results = []
    start_time = time.perf_counter()

    limits = httpx.Limits(
        max_connections=concurrency,
        max_keepalive_connections=concurrency,
    )

    async with httpx.AsyncClient(limits=limits) as client:
        for batch_start in range(0, total_requests, concurrency):
            batch_end = min(batch_start + concurrency, total_requests)

            tasks = [
                send_one_request(client, request_id=i)
                for i in range(batch_start, batch_end)
            ]

            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)

            print(f"已完成: {len(results)} / {total_requests}")

    end_time = time.perf_counter()
    total_time_s = end_time - start_time

    success_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]

    latencies = [r["latency_ms"] for r in success_results]

    total_prompt_tokens = sum(r["prompt_tokens"] for r in success_results)
    total_completion_tokens = sum(r["completion_tokens"] for r in success_results)
    total_tokens = sum(r["total_tokens"] for r in success_results)

    success_count = len(success_results)
    failed_count = len(failed_results)

    qps = total_requests / total_time_s if total_time_s > 0 else 0
    success_rate = success_count / total_requests if total_requests > 0 else 0
    tokens_per_second = total_completion_tokens / total_time_s if total_time_s > 0 else 0

    print("\n" + "=" * 60)
    print("压测结果")
    print("=" * 60)
    print(f"总请求数: {total_requests}")
    print(f"成功请求数: {success_count}")
    print(f"失败请求数: {failed_count}")
    print(f"成功率: {success_rate:.2%}")
    print(f"总耗时: {total_time_s:.2f} s")
    print(f"QPS: {qps:.2f} req/s")

    if latencies:
        print(f"平均延迟: {statistics.mean(latencies):.2f} ms")
        print(f"P50 延迟: {percentile(latencies, 50):.2f} ms")
        print(f"P95 延迟: {percentile(latencies, 95):.2f} ms")
        print(f"P99 延迟: {percentile(latencies, 99):.2f} ms")
        print(f"最小延迟: {min(latencies):.2f} ms")
        print(f"最大延迟: {max(latencies):.2f} ms")

    print(f"总 prompt tokens: {total_prompt_tokens}")
    print(f"总 completion tokens: {total_completion_tokens}")
    print(f"总 tokens: {total_tokens}")
    print(f"输出 tokens/s: {tokens_per_second:.2f}")

    if failed_results:
        print("\n失败请求示例:")
        for item in failed_results[:3]:
            print(item)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark /api/chat")
    parser.add_argument("--total", type=int, default=20, help="总请求数")
    parser.add_argument("--concurrency", type=int, default=1, help="并发数")
    parser.add_argument("--max-tokens", type=int, default=128, help="最大生成 token 数")

    args = parser.parse_args()

    asyncio.run(
        run_benchmark(
            total_requests=args.total,
            concurrency=args.concurrency,
        )
    )