import json
import time
import requests


API_URL = "http://127.0.0.1:8080/api/chat"


def main():
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "请用三句话解释什么是 vLLM。"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }

    print("正在请求 /api/chat ...")
    start_time = time.perf_counter()

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=120
        )

        end_time = time.perf_counter()

        print("HTTP 状态码:", response.status_code)
        print("客户端总耗时 ms:", round((end_time - start_time) * 1000, 2))

        try:
            data = response.json()
            print("响应 JSON:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            print("响应文本:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("连接失败：请确认 FastAPI 是否已经启动在 http://127.0.0.1:8080")

    except requests.exceptions.Timeout:
        print("请求超时：模型生成时间过长，或者服务没有正常返回")

    except Exception as e:
        print("请求异常:", repr(e))


if __name__ == "__main__":
    main()
