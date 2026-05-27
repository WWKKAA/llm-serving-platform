import time
import requests


API_URL = "http://127.0.0.1:8080/api/chat/stream"


def main():
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "请用五句话解释 PagedAttention。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }

    print("正在请求 /api/chat/stream ...")
    print("模型输出：")
    print("-" * 50)

    start_time = time.perf_counter()
    first_chunk_time = None

    try:
        with requests.post(
            API_URL,
            json=payload,
            stream=True,
            timeout=120
        ) as response:
            print("HTTP 状态码:", response.status_code)

            if response.status_code != 200:
                print("请求失败:")
                print(response.text)
                return

            for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                if chunk:
                    if first_chunk_time is None:
                        first_chunk_time = time.perf_counter()
                        ttft_ms = round((first_chunk_time - start_time) * 1000, 2)
                        print(f"\n[客户端测得 TTFT: {ttft_ms} ms]\n")

                    print(chunk, end="", flush=True)

        end_time = time.perf_counter()
        total_time_ms = round((end_time - start_time) * 1000, 2)

        print("\n" + "-" * 50)
        print("流式请求总耗时 ms:", total_time_ms)

    except requests.exceptions.ConnectionError:
        print("连接失败：请确认 FastAPI 是否已经启动在 http://127.0.0.1:8080")

    except requests.exceptions.Timeout:
        print("请求超时：模型生成时间过长，或者服务没有正常返回")

    except Exception as e:
        print("请求异常:", repr(e))


if __name__ == "__main__":
    main()
