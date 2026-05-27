import os


class Settings:
    # vLLM OpenAI-compatible API 地址
    VLLM_BASE_URL: str = os.getenv("VLLM_BASE_URL", "http://127.0.0.1:8000/v1")

    # vLLM 启动时暴露出来的模型名
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen2.5-0.5B-Instruct")

    # 本地服务端口
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8080"))

    # 默认生成参数
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "512"))

    # OpenAI client 需要 api_key 字段，本地 vLLM 可以随便填
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "EMPTY")

    # 日志目录
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")


settings = Settings()