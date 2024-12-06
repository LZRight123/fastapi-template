#!/bin/bash
set -e

# 启动应用
 if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    # 计算总 worker 数
    CORES=$(nproc)
    WORKERS_PER_CORE=${WORKERS_PER_CORE:-1}  # 如果未设置，默认为1
    WORKERS=$((CORES * WORKERS_PER_CORE))

    echo "生产或测试环境启动: http://0.0.0.0:80  Control+C 停止"
    exec uvicorn app.main:app --host 0.0.0.0 --port 80 --workers $WORKERS
 else
    exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 # --workers $WORKERS
 fi