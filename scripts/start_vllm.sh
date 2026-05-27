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
