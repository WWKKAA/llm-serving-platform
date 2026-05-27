# 系统架构

## 项目名称

基于 vLLM 的本地大模型推理服务平台

## 总体架构

```text
Client
  |
  | HTTP 请求
  v
FastAPI Backend
  |
  | OpenAI-compatible API 调用
  v
vLLM Server
  |
  | GPU 推理
  v
Qwen2.5-0.5B-Instruct
```