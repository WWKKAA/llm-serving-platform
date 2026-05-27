# API 文档

## 1. 基本信息

项目名称：基于 vLLM 的本地大模型推理服务平台

FastAPI 服务地址：

```text
http://127.0.0.1:8080
```

vLLM 服务地址：

```text
http://127.0.0.1:8000/v1
```

当前模型：

```text
Qwen2.5-0.5B-Instruct
```

---

## 2. 接口列表

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/api/chat` | 普通问答，一次性返回完整回答 |
| POST | `/api/chat/stream` | 流式问答，逐 chunk 返回模型输出 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/metrics` | 基础指标统计 |

---

## 3. 普通问答接口

### 3.1 接口说明

```text
POST /api/chat
```

该接口接收用户问题，调用 vLLM 推理服务，并在模型生成完成后一次性返回完整回答。

---

### 3.2 请求示例

```bash
curl -X POST "http://127.0.0.1:8080/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "请用三句话解释什么是 vLLM"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 128
  }'
```

---

### 3.3 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `messages` | array | 是 | 对话消息列表 |
| `messages[].role` | string | 是 | 消息角色，常用 `system`、`user`、`assistant` |
| `messages[].content` | string | 是 | 消息内容 |
| `temperature` | float | 否 | 采样温度，值越大输出越随机 |
| `max_tokens` | int | 否 | 最大生成 token 数 |

---

### 3.4 响应示例

```json
{
  "request_id": "3f2a1c7e-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "model": "Qwen2.5-0.5B-Instruct",
  "content": "vLLM 是一个用于大模型推理加速的框架。它通过高效的 KV Cache 管理和连续批处理提升推理吞吐量。它常用于构建高并发的大模型服务。",
  "prompt_tokens": 18,
  "completion_tokens": 56,
  "total_tokens": 74,
  "latency_ms": 1234.56
}
```

---

### 3.5 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `request_id` | string | 请求唯一 ID，便于日志追踪 |
| `model` | string | 当前使用的模型名称 |
| `content` | string | 模型生成的完整回答 |
| `prompt_tokens` | int | 输入 token 数 |
| `completion_tokens` | int | 输出 token 数 |
| `total_tokens` | int | 总 token 数 |
| `latency_ms` | float | 请求耗时，单位毫秒 |

---

## 4. 流式问答接口

### 4.1 接口说明

```text
POST /api/chat/stream
```

该接口用于流式输出。模型生成过程中，服务会逐步返回内容，适合聊天机器人等需要更快首字响应的场景。

---

### 4.2 请求示例

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

也可以使用测试脚本：

```bash
python scripts/test_stream.py
```

---

### 4.3 请求参数

与 `/api/chat` 相同。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `messages` | array | 是 | 对话消息列表 |
| `temperature` | float | 否 | 采样温度 |
| `max_tokens` | int | 否 | 最大生成 token 数 |

---

### 4.4 响应格式

响应类型：

```text
text/plain
```

返回内容会分多次 chunk 输出。

示例：

```text
PagedAttention 是 vLLM 中用于优化 KV Cache 管理的核心技术...
```

说明：

- `/api/chat`：等待完整回答生成后一次性返回 JSON。
- `/api/chat/stream`：模型边生成，服务边返回文本片段。
- 流式输出可以降低首字等待时间，但不一定减少总生成耗时。

---

## 5. 健康检查接口

### 5.1 接口说明

```text
GET /api/health
```

用于检查 FastAPI 服务和 vLLM 服务是否正常。

---

### 5.2 请求示例

```bash
curl http://127.0.0.1:8080/api/health
```

---

### 5.3 响应示例

```json
{
  "status": "ok",
  "fastapi": "ok",
  "vllm": "ok",
  "vllm_base_url": "http://127.0.0.1:8000/v1",
  "model": "Qwen2.5-0.5B-Instruct"
}
```

---

### 5.4 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `status` | string | 整体服务状态，`ok` 表示正常，`degraded` 表示部分异常 |
| `fastapi` | string | FastAPI 服务状态 |
| `vllm` | string | vLLM 服务状态 |
| `vllm_base_url` | string | vLLM API 地址 |
| `model` | string | 当前模型名称 |

---

## 6. 基础指标接口

### 6.1 接口说明

```text
GET /api/metrics
```

用于查看当前服务的基础请求统计信息。

---

### 6.2 请求示例

```bash
curl http://127.0.0.1:8080/api/metrics
```

---

### 6.3 响应示例

```json
{
  "total_requests": 10,
  "success_requests": 9,
  "failed_requests": 1,
  "failed_rate": 0.1,
  "avg_latency_ms": 856.32
}
```

---

### 6.4 响应字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `total_requests` | int | 总请求数 |
| `success_requests` | int | 成功请求数 |
| `failed_requests` | int | 失败请求数 |
| `failed_rate` | float | 请求失败率 |
| `avg_latency_ms` | float | 平均响应延迟，单位毫秒 |

---

## 7. 常见状态码

| 状态码 | 说明 |
|---|---|
| `200` | 请求成功 |
| `422` | 请求参数格式错误 |
| `500` | 服务内部错误，通常是 vLLM 调用失败或模型推理异常 |

---

## 8. 测试命令汇总

启动 vLLM：

```bash
bash scripts/start_vllm.sh
```

启动 FastAPI：

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

测试健康检查：

```bash
curl http://127.0.0.1:8080/api/health
```

测试普通问答：

```bash
python scripts/test_api.py
```

测试流式输出：

```bash
python scripts/test_stream.py
```

查看基础指标：

```bash
curl http://127.0.0.1:8080/api/metrics
```

查看日志：

```bash
tail -f logs/server.log
```
