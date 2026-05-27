import time
import requests


API_URL = "http://127.0.0.1:8080/api/chat/stream"


def test_stream_once():
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "请用五句话解释 PagedAttention。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }

    start_time = time.perf_counter()
    first_chunk_time = None
    chunk_count = 0
    output_chars = 0

    with requests.post(
        API_URL,
        json=payload,
        stream=True,
        timeout=120,
    ) as response:
        if response.status_code != 200:
            print("请求失败:", response.status_code)
            print(response.text)
            return

        for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
            if chunk:
                if first_chunk_time is None:
                    first_chunk_time = time.perf_counter()

                chunk_count += 1
                output_chars += len(chunk)
                print(chunk, end="", flush=True)

    end_time = time.perf_counter()

    ttft_ms = (
        (first_chunk_time - start_time) * 1000
        if first_chunk_time is not None
        else 0
    )
    total_time_ms = (end_time - start_time) * 1000

    print("\n" + "=" * 60)
    print(f"TTFT: {ttft_ms:.2f} ms")
    print(f"总耗时: {total_time_ms:.2f} ms")
    print(f"chunk 数量: {chunk_count}")
    print(f"输出字符数: {output_chars}")
    print("=" * 60)


if __name__ == "__main__":
    test_stream_once()