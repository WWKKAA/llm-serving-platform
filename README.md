# 基于 vLLM 的本地大模型推理服务平台

## 1. 项目简介

本项目基于 **FastAPI + vLLM** 构建本地大模型推理服务平台。

项目将 vLLM 提供的 OpenAI-compatible API 进一步封装为统一的后端服务接口，支持普通问答、流式输出、健康检查、基础 metrics、请求日志和响应时间统计。

当前版本主要目标是完成一个可运行、可复现、可扩展的 LLM Serving 项目雏形，为后续并发压测、性能分析、监控接入和工程化部署打基础。

---

## 2. 当前版本

当前版本：`v0.1.0`

已完成功能：

- vLLM 本地模型服务启动
- FastAPI 后端服务封装
- 普通问答接口 `/api/chat`
- 流式输出接口 `/api/chat/stream`
- 健康检查接口 `/api/health`
- 基础指标接口 `/api/metrics`
- 请求耗时统计
- prompt tokens / completion tokens 统计
- request_id 请求追踪
- 控制台日志与文件日志
- FlashInfer sampler 报错排查记录
- 环境依赖文件保存

---

## 3. 项目环境

### 3.1 硬件环境

当前测试环境：

| 项目 | 配置 |
|---|---|
| 平台 | AutoDL |
| GPU | NVIDIA RTX 4090 24GB |
| 模型 | Qwen/Qwen2.5-0.5B-Instruct |
| 本地模型路径 | `/root/autodl-tmp/models/Qwen2.5-0.5B-Instruct` |

### 3.2 软件环境

当前使用的 Conda 环境：

```bash
conda activate vllm-demo
```

主要依赖：

- Python
- FastAPI
- Uvicorn
- vLLM
- OpenAI Python SDK
- Pydantic
- Requests

安装依赖：

```bash
pip install -r requirements.txt
```

或者使用 Conda 环境文件恢复：

```bash
conda env create -f environment.yml
```

---

## 4. 项目结构

```text
llm-serving-platform/
├── backend/
│   ├── main.py
│   ├── vllm_client.py
│   ├── schemas.py
│   ├── logger.py
│   └── config.py
├── scripts/
│   ├── start_vllm.sh
│   ├── test_api.py
│   └── test_stream.py
├── docs/
│   ├── architecture.md
│   └── api.md
├── logs/
├── requirements.txt
├── environment.yml
└── README.md
```

### 4.1 `backend/`

后端服务核心代码目录。

| 文件 | 作用 |
|---|---|
| `main.py` | FastAPI 服务入口，定义 `/api/chat`、`/api/chat/stream`、`/api/health`、`/api/metrics` |
| `vllm_client.py` | 封装对 vLLM OpenAI-compatible API 的调用 |
| `schemas.py` | 使用 Pydantic 定义请求和响应结构 |
| `logger.py` | 统一日志配置，支持控制台和文件日志 |
| `config.py` | 项目配置中心，管理 vLLM 地址、模型名、默认生成参数等 |

### 4.2 `scripts/`

项目启动和测试脚本目录。

| 文件 | 作用 |
|---|---|
| `start_vllm.sh` | 启动 vLLM 模型服务 |
| `test_api.py` | 测试普通问答接口 `/api/chat` |
| `test_stream.py` | 测试流式输出接口 `/api/chat/stream` |

### 4.3 `docs/`

项目文档目录。

| 文件 | 作用 |
|---|---|
| `architecture.md` | 系统架构说明 |
| `api.md` | API 接口说明 |

### 4.4 `logs/`

日志目录。

运行服务后会生成：

```text
logs/server.log
```

日志中记录：

- request_id
- 请求状态
- prompt 字符数
- prompt tokens
- completion tokens
- 响应耗时
- 错误信息

---

## 5. 系统架构

整体调用链路如下：

```text
Client
  |
  | HTTP 请求
  v
FastAPI Backend
  |
  | OpenAI-compatible API
  v
vLLM Server
  |
  | GPU 推理
  v
Qwen2.5-0.5B-Instruct
```

FastAPI 和 vLLM 的关系：

- vLLM 负责高性能模型推理。
- FastAPI 负责业务接口封装、参数校验、日志、metrics 和异常处理。
- 用户或业务系统只需要访问 FastAPI 暴露的接口，不需要直接调用 vLLM 原生接口。

---

## 6. 为什么需要 FastAPI 封装 vLLM？

vLLM 已经提供了 OpenAI-compatible API，但在实际工程中，业务方通常不直接调用底层推理服务。

增加 FastAPI 封装层后，可以实现：

1. 统一 API 格式
2. 统一参数校验
3. 统一异常处理
4. 请求日志记录
5. request_id 链路追踪
6. 响应时间统计
7. 基础 metrics 统计
8. 后续方便扩展鉴权、限流、压测和监控

因此，本项目的核心不是简单调用模型，而是完成一个具备基本工程结构的 LLM Serving 后端服务。

---

## 7. 启动 vLLM 服务

### 7.1 启动命令

进入项目目录：

```bash
cd ~/llm-serving-platform
```

启动 vLLM：

```bash
bash scripts/start_vllm.sh
```

当前 `scripts/start_vllm.sh` 内容示例：

```bash
#!/bin/bash

source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo

export VLLM_USE_FLASHINFER_SAMPLER=0

MODEL_PATH="/root/autodl-tmp/models/Qwen2.5-0.5B-Instruct"
SERVED_MODEL_NAME="Qwen2.5-0.5B-Instruct"

vllm serve $MODEL_PATH \
  --served-model-name $SERVED_MODEL_NAME \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.85
```

### 7.2 验证 vLLM 是否启动成功

新开一个终端，执行：

```bash
curl http://127.0.0.1:8000/v1/models
```

正常情况下会返回模型列表，例如：

```json
{
  "object": "list",
  "data": [
    {
      "id": "Qwen2.5-0.5B-Instruct",
      "object": "model",
      "owned_by": "vllm",
      "root": "/root/autodl-tmp/models/Qwen2.5-0.5B-Instruct"
    }
  ]
}
```

---

## 8. 启动 FastAPI 后端服务

新开一个终端，执行：

```bash
cd ~/llm-serving-platform

source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo

uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

启动成功后，FastAPI 服务地址为：

```text
http://127.0.0.1:8080
```

此时两个服务分别是：

| 服务 | 地址 |
|---|---|
| vLLM | `http://127.0.0.1:8000/v1` |
| FastAPI | `http://127.0.0.1:8080` |

---

## 9. API 接口说明

### 9.1 普通问答接口

接口：

```text
POST /api/chat
```

请求示例：

```bash
curl -X POST "http://127.0.0.1:8080/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "请用三句话解释什么是 FastAPI"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 128
  }'
```

响应字段示例：

```json
{
  "request_id": "xxxx",
  "model": "Qwen2.5-0.5B-Instruct",
  "content": "FastAPI 是一个用于构建 Web API 的 Python 框架……",
  "prompt_tokens": 20,
  "completion_tokens": 80,
  "total_tokens": 100,
  "latency_ms": 1234.56
}
```

---

### 9.2 流式输出接口

接口：

```text
POST /api/chat/stream
```

请求示例：

```bash
curl -X POST "http://127.0.0.1:8080/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "请用五句话解释 PagedAttention"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

说明：

- `/api/chat` 会等待模型完整生成后一次性返回。
- `/api/chat/stream` 会在模型生成过程中逐 chunk 返回内容。
- 流式输出可以降低用户感知等待时间，但不一定缩短总生成时间。

---

### 9.3 健康检查接口

接口：

```text
GET /api/health
```

请求：

```bash
curl http://127.0.0.1:8080/api/health
```

响应示例：

```json
{
  "status": "ok",
  "fastapi": "ok",
  "vllm": "ok",
  "vllm_base_url": "http://127.0.0.1:8000/v1",
  "model": "Qwen2.5-0.5B-Instruct"
}
```

说明：

- `fastapi` 表示后端服务状态。
- `vllm` 表示 vLLM 推理服务是否可访问。
- `status=ok` 表示整体服务正常。
- `status=degraded` 表示 FastAPI 可访问，但 vLLM 可能不可用。

---

### 9.4 基础指标接口

接口：

```text
GET /api/metrics
```

请求：

```bash
curl http://127.0.0.1:8080/api/metrics
```

响应示例：

```json
{
  "total_requests": 10,
  "success_requests": 9,
  "failed_requests": 1,
  "failed_rate": 0.1,
  "avg_latency_ms": 856.32
}
```

当前 metrics 统计内容：

| 指标 | 含义 |
|---|---|
| `total_requests` | 总请求数 |
| `success_requests` | 成功请求数 |
| `failed_requests` | 失败请求数 |
| `failed_rate` | 请求失败率 |
| `avg_latency_ms` | 平均响应延迟 |

---

## 10. 测试脚本

### 10.1 测试普通问答接口

```bash
python scripts/test_api.py
```

该脚本会请求：

```text
POST http://127.0.0.1:8080/api/chat
```

并打印：

- HTTP 状态码
- 客户端总耗时
- JSON 响应内容

---

### 10.2 测试流式输出接口

```bash
python scripts/test_stream.py
```

该脚本会请求：

```text
POST http://127.0.0.1:8080/api/chat/stream
```

并逐 chunk 打印模型输出，同时统计客户端侧 TTFT 和总耗时。

---

## 11. 日志查看

查看服务日志：

```bash
tail -f logs/server.log
```

日志示例：

```text
2026-05-27 15:30:01 | INFO | request_id=xxx | status=success | prompt_chars=20 | prompt_tokens=15 | completion_tokens=80 | latency_ms=1234.56
```

日志中不建议保存：

- 完整 prompt
- 完整模型回答
- API key
- 用户隐私数据
- 业务敏感信息

当前项目只记录 prompt 长度、token 数、请求状态和耗时，便于后续压测分析。

---

## 12. 完整运行流程

### 12.1 启动 vLLM

终端 1：

```bash
cd ~/llm-serving-platform
bash scripts/start_vllm.sh
```

验证：

```bash
curl http://127.0.0.1:8000/v1/models
```

---

### 12.2 启动 FastAPI

终端 2：

```bash
cd ~/llm-serving-platform

source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo

uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

---

### 12.3 运行测试

终端 3：

```bash
cd ~/llm-serving-platform

source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo

curl http://127.0.0.1:8080/api/health
python scripts/test_api.py
python scripts/test_stream.py
curl http://127.0.0.1:8080/api/metrics
```

---

## 13. 常见问题与排错记录

### 13.1 `vllm: command not found`

问题表现：

```text
scripts/start_vllm.sh: line 6: vllm: command not found
```

原因：

当前终端没有激活安装 vLLM 的 Conda 环境。

解决方法：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo
which vllm
```

或者在 `scripts/start_vllm.sh` 中加入：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo
```

---

### 13.2 `conda activate` 无法使用

问题表现：

```text
CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'
```

解决方法：

```bash
source /root/miniconda3/etc/profile.d/conda.sh
conda activate vllm-demo
```

也可以初始化 shell：

```bash
conda init bash
source ~/.bashrc
```

---

### 13.3 FlashInfer sampler 编译失败

问题表现：

```text
nvcc fatal: Unsupported gpu architecture 'compute_89'
RuntimeError: Ninja build failed
```

原因：

RTX 4090 对应 Ada 架构，FlashInfer 在编译 sampler 时尝试使用 `compute_89 / sm_89`，但当前容器中的 CUDA Toolkit / nvcc 不支持该架构，导致编译失败。

解决方法：

在 `scripts/start_vllm.sh` 中禁用 FlashInfer sampler：

```bash
export VLLM_USE_FLASHINFER_SAMPLER=0
```

清理缓存后重新启动：

```bash
rm -rf ~/.cache/flashinfer
rm -rf ~/.cache/vllm/torch_compile_cache

bash scripts/start_vllm.sh
```

---

### 13.4 FastAPI 无法连接 vLLM

先检查 vLLM 是否正常：

```bash
curl http://127.0.0.1:8000/v1/models
```

如果该命令失败，说明问题在 vLLM 服务侧，而不是 FastAPI。

如果 vLLM 正常，再检查 FastAPI 配置：

```bash
cat backend/config.py
```

确认：

```text
VLLM_BASE_URL=http://127.0.0.1:8000/v1
MODEL_NAME=Qwen2.5-0.5B-Instruct
```

---

### 13.5 端口被占用

问题表现：

```text
Address already in use
```

查看占用端口的进程：

```bash
lsof -i:8000
lsof -i:8080
```

结束进程：

```bash
kill -9 <PID>
```

---

## 14. 当前项目成果

本项目已经实现了一个基础可用的 LLM Serving 后端系统。

当前完整链路：

```text
测试脚本 / curl
    ↓
FastAPI Backend
    ↓
vLLM OpenAI-compatible API
    ↓
Qwen2.5-0.5B-Instruct
    ↓
返回普通或流式模型输出
```

已具备：

- 本地模型推理服务
- 后端接口封装
- 普通问答能力
- 流式输出能力
- 服务健康检查
- 基础运行指标
- 请求日志追踪
- 环境可复现能力

---

## 15. 后续优化方向

后续计划进入压测与监控阶段，主要包括：

1. 并发请求压测
2. 平均延迟统计
3. P95 / P99 延迟统计
4. TTFT 测量
5. tokens/s 统计
6. 不同 `max_tokens` 对响应时间的影响
7. 不同并发数对吞吐量的影响
8. GPU 显存和利用率监控
9. Prometheus / Grafana 监控接入
10. Docker 化部署
11. API Key 鉴权
12. 请求限流
13. 多模型切换

后续可新增目录：

```text
benchmark/
├── benchmark_api.py
├── benchmark_stream.py
└── benchmark_report.md
```



