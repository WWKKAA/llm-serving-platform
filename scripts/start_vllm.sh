#!/bin/bash

MODEL_PATH="/root/autodl-tmp/models/Qwen2.5-0.5B-Instruct"
SERVED_MODEL_NAME="Qwen2.5-0.5B-Instruct"

vllm serve $MODEL_PATH \
  --served-model-name $SERVED_MODEL_NAME \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype auto \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.85